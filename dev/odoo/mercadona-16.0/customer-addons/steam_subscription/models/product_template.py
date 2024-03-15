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
            pass
            # self.create_subscription_variants()
        else:
            pass
            # self.remove_subscription_variants()

    def create_subscription_variants(self):
        subscription_attribute = self.env.ref('steam_subscription.product_subscription_attribute')
        subscription_values = self.env['product.attribute.value'].search([('attribute_id', '=', subscription_attribute.id)])

        for value in subscription_values:
            variant_name = f"{value.name} Subscription"
            existing_variant = self.env['product.product'].search([('name', '=', variant_name)])
            if not existing_variant:
                variant_vals = {
                    'name': variant_name,
                    'product_tmpl_id': self.id,
                    'product_template_attribute_value_ids': [(0, 0, {
                        'product_attribute_value_id': value.id,
                        'attribute_line_id': value.attribute_line_id.id,  # Set attribute_line_id
                    })]
                }
                self.env['product.product'].create(variant_vals)

    def remove_subscription_variants(self):
        subscription_variants = self.env['product.product'].search([
            ('product_tmpl_id', '=', self.id),
            ('product_template_attribute_value_ids.attribute_id', '=', self.env.ref('steam_subscription.product_subscription_attribute').id)
        ])
        subscription_variants.unlink()

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
