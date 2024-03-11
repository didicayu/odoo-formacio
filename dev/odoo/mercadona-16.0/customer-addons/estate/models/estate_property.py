from odoo import fields, models, api, exceptions
from odoo.tools import float_utils
from odoo.tools.translate import _


class EstateProperty(models.Model):
    _name = "estate_property"
    _inherit = ['mail.thread']
    _description = "Real Estate Properties"
    _order = "id desc"

    name = fields.Char(required=True, default="Unknown")
    description = fields.Text()
    property_type_id = fields.Many2one("estate_property_type",
                                       string="Property Type")  # This is a many2one field that will link to the estate_property_type model
    property_tag_ids = fields.Many2many("estate_property_tag",
                                        string="Tags")  # This is a many2many field that will link to the estate_property_tag model
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), months=3))

    best_offer = fields.Float(compute="_compute_best_offer", store=True)

    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    )

    total_area = fields.Integer(compute="_compute_total_area", store=True)

    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="Status",
        selection=[("new", "New"), ("offer_received", "Offer Received"), ("offer_accepted", "Offer Accepted"),
                   ("sold", "Sold"), ("canceled", "Canceled")],
        required=True,
        copy=False,
        default="new",
        tracking=True
    )

    salesman_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user, tracking=True)
    # using default=self.env.user directly might cause issues because the default parameter in the field definition expects a callable 
    # (like a function or lambda) that returns the default value.

    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)

    offer_ids = fields.One2many("estate_property_offer", "property_id", string="Offers")

    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price >= 0)", "The expected price must be positive."),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive.")
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped("price"), default=0.0)

    @api.onchange("garden")
    def _onchange_garden(self):
        self.ensure_one()
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False

        else:
            self.garden_area = 10
            self.garden_orientation = "north"

    def sell_property(self):

        for property in self:
            if property.state == "canceled":
                raise exceptions.UserError("You cannot sell a canceled property.")

            property.state = "sold"

        return True  # A public method should always return something, when in doubt, return True.

    def cancel_property(self):

        for property in self:
            if property.state == "sold":
                raise exceptions.UserError("You cannot cancel a sold property.")

            property.state = "canceled"

        return True

    @api.constrains("selling_price")
    def _selling_price_constraint(self):

        for property in self:
            if property.selling_price < property.expected_price * 0.9 and not float_utils.float_is_zero(
                    property.selling_price, 6):
                raise exceptions.ValidationError("The selling price cannot be less than 90% of the expected price.")

    @api.ondelete(at_uninstall=False)
    def _avoid_unwanted_offer_deletions(self):
        for record in self:
            if record.state != 'new' and record.state != 'canceled':
                raise exceptions.UserError("can't delete a property if its state is not “New” or “Canceled")

    @api.model
    def _track_subtype(self, init_values):
        # init_values contains the modified fields' values before the changes
        self.ensure_one()
        if 'state' in init_values and self.state == 'sold':
            return self.env.ref('estate.mt_state_change')
        return super(EstateProperty, self)._track_subtype(init_values)

    def _notify_get_groups(self, message, groups):
        groups = super(EstateProperty, self)._notify_get_groups(message, groups)

        self.ensure_one()
        if self.state == 'sold':
            app_action = self._notify_get_action_link('method', method='cancel_property')
            property_actions = [{'url': app_action, 'title': _('Cancel')}]

        new_group = (
            'property_manager',
            lambda partner: bool(partner.user_ids) and
                            any(user.has_group('estate.property_manager')
                                for user in partner.user_ids),
            {
                'actions': property_actions,
            })

        return [new_group] + groups
