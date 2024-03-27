from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    games_ids = fields.Many2many('product.product', string='VideoGames')
