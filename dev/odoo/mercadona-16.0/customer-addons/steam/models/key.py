import random
import string

from odoo import fields, models, api


class Key(models.Model):
    _name = "steam.key"

    key_code = fields.Char(readonly=True)
    validity_deadline = fields.Date(string="Key's Validity", default=fields.Date.add(fields.date.today(), years=10))

    game_id = fields.Many2one("product.product", string="Game", required=True)
    user_id = fields.Many2one('res.users', string="User", required=True)

    def _compute_key(self):
        key_format = "ABCD1-EFGHI-JKLM2-NOPQR-STU34"

        fake_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(key_format)))

        # Insert dashes in the key format
        formatted_fake_key = '-'.join([fake_key[i:i + 5] for i in range(0, len(fake_key), 5)])

        return formatted_fake_key

    @api.model
    def create(self, vals):
        # generate key on creation
        vals['key_code'] = self._compute_key()

        return super().create(vals)
