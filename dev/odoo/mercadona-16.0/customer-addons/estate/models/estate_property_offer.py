from odoo import fields, models, api, exceptions

class EstatePropertyOffer(models.Model):
    _name = "estate_property_offer"
    _description = "Real Estate Property Offers"
    _order = "price desc"
    
    price = fields.Float()
    status = fields.Selection(
        string = "Status",
        selection = [("accepted", "Accepted"), ("refused", "Refused"), ("pending", "Pending")],
        required = True,
        default = "pending",
        copy = False
    )
    
    validity = fields.Integer(string="Validity (in days)", default=7, compute="_inverse_date_deadline", inverse="_compute_date_deadline",store=True)
    date_deadline = fields.Date(string="Deadline", required=True, copy=False, compute="_compute_date_deadline", inverse="_inverse_date_deadline",store=True)
    
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate_property", string="Property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    
    _sql_constraints = [
        ("check_offer_price", "CHECK(price >= 0)", "The offer price must be positive.")
    ]
    
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)

    @api.depends("create_date", "date_deadline")
    def _inverse_date_deadline(self):
        for record in self:
            
            if record.create_date:    
                record.validity = fields.Date.subtract(record.date_deadline, record.create_date).day
    
    @api.depends("property_id")
    def accept_offer(self):
        for offer in self:
            if offer.property_id and offer.property_id.state == "offer_accepted":
                raise exceptions.UserError("You cannot accept an offer on a property that has another accepted offer.")
            
            offer.status = "accepted"
            offer.property_id.state = "offer_accepted"
            offer.property_id.selling_price = offer.price
    
    @api.depends("property_id")
    def decline_offer(self):
        for offer in self:
            
            if offer.status == "accepted":
                offer.property_id.state = "offer_received"
            
            offer.status = "refused"

    @api.model
    def create(self, vals):
        estate_property = self.env['estate_property'].browse(vals.get('property_id'))

        existing_offers = estate_property.offer_ids

        for offer in existing_offers:
            if offer.price > vals['price']:
                raise exceptions.UserError("Can't create an offer with a lower price than an existing one")

        if estate_property:
            estate_property.write({'state': 'offer_received'})

        return super().create(vals)
