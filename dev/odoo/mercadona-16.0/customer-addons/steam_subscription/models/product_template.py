from odoo import models, fields, api

SUBSCRIPTION_TYPES = [
    ('1_month', '1 Month Subscription'),
    ('2_months', '2 Months Subscription'),
    ('3_months', '3 Months Subscription'),
    ('12_months', '12 Months Subscription'),
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription = fields.Boolean(string="Is a Subscription", default=False)
    subscription_type = fields.Selection(
        SUBSCRIPTION_TYPES,
        string='Subscription Type')

    @api.onchange('is_subscription')
    def _onchange_is_subscription(self):
        if self.is_subscription:
            self._create_subscription_variants()

    def _create_subscription_variants(self):
        for key, value in SUBSCRIPTION_TYPES:
            variant = self.env['product.product'].create({
                'name': value,
                'product_tmpl_id': self.id,
                # Add any other fields you want to set for the variant
            })
