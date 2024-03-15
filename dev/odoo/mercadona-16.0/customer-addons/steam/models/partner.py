from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    game_ids = fields.Many2many('product.product', string="VideoGames")

    is_franchise = fields.Boolean(string='Is Franchise')
