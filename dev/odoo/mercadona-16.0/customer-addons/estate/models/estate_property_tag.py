from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate_property_tag"
    _description = "Real Estate Property Tags"
    _order = "name"
    
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name of the tag must be unique.")
    ]
    
    name = fields.Char(required=True)
    color = fields.Integer()
