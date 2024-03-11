from odoo import models, fields


class Tag(models.Model):
    _name = "steam.tag"
    _description = "Steam's VideoGames tags"
    _order = "name"

    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name of the tag must be unique.")
    ]

    name = fields.Char(required=True, string="Game Tag")
    color = fields.Integer()
