from odoo import fields, models, api, _


class InheritedUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate_property", "salesman_id", string="Properties",
                                   domain=[('active', '=', 'True')])

