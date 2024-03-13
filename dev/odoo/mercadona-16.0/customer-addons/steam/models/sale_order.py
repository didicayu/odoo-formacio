from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    game_ids = fields.Many2many('product.product', string='Video Games')
