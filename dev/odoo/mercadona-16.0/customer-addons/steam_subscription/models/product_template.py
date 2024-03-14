from odoo import models, fields, api

SUBSCRIPTION_TYPES = [
    ('1_month', '1 Month Subscription'),
    ('3_months', '3 Months Subscription'),
    ('6_months', '6 Months Subscription'),
    ('12_months', '12 Months Subscription'),
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription = fields.Boolean(string="Is a Subscription", default=False)
    subscription_type = fields.Selection(
        SUBSCRIPTION_TYPES,
        string='Subscription Type')

    # TODO fecha inicio y fecha de fin variable, enviar mail cuando queden 5 dias para finalizar subscripción

    @api.onchange('is_subscription')
    def _onchange_is_subscription(self):
        if self.is_subscription:
            self.access_data()

    def access_data(self):
        subscription_attribute = self.env.ref('steam_subscription.product_subscription_attribute')
        subscription_values = self.env['product.attribute.value'].search(
            [('attribute_id', '=', subscription_attribute.id)])

        print("------------Subscription Variants---------------")
        for value in subscription_values:
            print("Name:", value.name)
            print("Attribute:", value.attribute_id.name)
            print("Sequence:", value.sequence)
            print("\n")
