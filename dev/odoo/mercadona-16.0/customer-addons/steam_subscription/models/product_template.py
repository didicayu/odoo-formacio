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

    @api.model
    def send_subscription_expiry_notifications(self):
        # Fetch subscriptions expiring in 5 days
        expiry_date_limit = fields.Date.add(fields.Date.today(), days=5)
        expiring_keys = self.env['steam.key'].search([
            ('validity_deadline', '=', expiry_date_limit)
        ])

        # Group expiring keys by user
        expiring_keys_by_user = {}
        for key in expiring_keys:
            if key.user_id not in expiring_keys_by_user:
                expiring_keys_by_user[key.user_id] = []
            expiring_keys_by_user[key.user_id].append(key)

        # Send email notifications for expiring keys
        for user, keys in expiring_keys_by_user.items():
            # Compose email content
            subject = "Your subscription is about to expire"
            body = f"Dear {user.name},\n\nYour subscription for the following games is ending soon:\n"
            for key in keys:
                body += f"- {key.game_id.name}, expiring on {key.validity_deadline}\n"
            body += "\nPlease renew your subscription to continue enjoying our services.\n\nBest regards,\nThe Subscription Team"

            # Send email
            user.message_post(
                body=body,
                subject=subject,
                partner_ids=[user.partner_id.id],
                subtype='mail.mt_comment'
            )

    @api.onchange('is_subscription')
    def _onchange_is_subscription(self):
        if self.is_subscription:
            self.create_subscription_variants()
        else:
            self.remove_subscription_variants()

    def create_subscription_variants(self):
        subscription_attribute = self.env.ref('steam_subscription.product_subscription_attribute')
        subscription_values = self.env['product.attribute.value'].search(
            [('attribute_id', '=', subscription_attribute.id)])

        if not self.attribute_line_ids.attribute_id.ids:
            attribute_line_vals = {
                'product_tmpl_id': self.id.origin,
                'attribute_id': subscription_attribute.id,
                'value_ids': [(6, 0, subscription_values.ids)]
            }
            self.env['product.template.attribute.line'].create(attribute_line_vals)

    def remove_subscription_variants(self):
        subscription_attribute = self.env.ref('steam_subscription.product_subscription_attribute')

        subscription_variants = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', self.id),
            ('attribute_id', '=', subscription_attribute.id)
        ])

        print("Search Results:", subscription_variants)

        if subscription_variants:
            for variant in subscription_variants:
                print("Variant ID:", variant.id)
                print("Variant Name:", variant.name)
                print("Attributes:", variant.attribute_value_ids.mapped('attribute_id.name'))

            subscription_variants.unlink()
            self.env['product.template.attribute.line'].search([
                ('product_tmpl_id', '=', self.id),
                ('attribute_id', '=', subscription_attribute.id),
            ]).unlink()
            print("Subscription variants and related attribute lines successfully removed.")
        else:
            print("No subscription variants found.")

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
