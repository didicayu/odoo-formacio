from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_franchise = fields.Boolean(string='Is Franchise')
