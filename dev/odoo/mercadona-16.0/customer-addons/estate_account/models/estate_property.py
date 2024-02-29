from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = "estate_property"

    def sell_property(self):
        print("I'm selling a property!")

        # Create a new move
        move_obj = self.env["account.move"]
        move_data = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'journal_id': 1,
        }

        move = move_obj.create(move_data)

        #Create a new move line
        move_line_obj = self.env["account.move.line"]
        move_line_data = {
            'move_id': move.id,
            'name': self.name,
            'quantity': 1,
            'price_unit': self.selling_price * 0.06,
            'account_id': 1,
        }

        move_line = move_line_obj.create(move_line_data)

        # Create administrative fees line
        fees_line_obj = self.env["account.move.line"]
        fees_line_data = {
            'move_id': move.id,
            'name': "Administrative Fees",
            'quantity': 1,
            'price_unit': 100,
            'account_id': 1,
        }

        fees_line = fees_line_obj.create(fees_line_data)

        return super().sell_property()