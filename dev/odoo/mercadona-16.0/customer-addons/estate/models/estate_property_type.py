from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate_property_type"
    _description = "Real Estate Property Types"
    _order = "sequence, name"
    
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name of the property type must be unique.")
    ]
    
    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default = 1)
    
    property_ids = fields.One2many("estate_property", "property_type_id", string="Properties") # This is a one2many field that will link to the estate_property model

    offer_ids = fields.One2many("estate_property_offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count")

    def _compute_offer_count(self):
        for record in self:
            self.offer_count = len(record.offer_ids)
