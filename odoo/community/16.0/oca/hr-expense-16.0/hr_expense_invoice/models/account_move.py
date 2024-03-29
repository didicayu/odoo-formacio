# Copyright 2019 Ecosoft <saranl@ecosoft.co.th>
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    expense_ids = fields.One2many(
        comodel_name="hr.expense", inverse_name="invoice_id", string="Expenses"
    )

    @api.constrains("amount_total")
    def _check_expense_ids(self):
        DecimalPrecision = self.env["decimal.precision"]
        precision = DecimalPrecision.precision_get("Product Price")
        for move in self.filtered("expense_ids"):
            expense_amount = sum(move.expense_ids.mapped("total_amount"))
            if float_compare(expense_amount, move.amount_total, precision) != 0:
                raise ValidationError(
                    _(
                        "You can't change the total amount, as there's an expense "
                        "linked to this invoice."
                    )
                )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains("account_id", "display_type")
    def _check_payable_receivable(self):
        _self = self.filtered("expense_id")
        return super(AccountMoveLine, (self - _self))._check_payable_receivable()
