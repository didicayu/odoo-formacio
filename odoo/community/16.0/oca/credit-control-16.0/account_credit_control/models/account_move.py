# Copyright 2012-2017 Camptocamp SA
# Copyright 2017 Okia SPRL (https://okia.be)
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Check on cancelling of an invoice"""

    _inherit = "account.move"

    credit_policy_id = fields.Many2one(
        comodel_name="credit.control.policy",
        string="Credit Control Policy",
        help="The Credit Control Policy used for this "
        "invoice. If nothing is defined, it will "
        "use the account setting or the partner "
        "setting.",
        readonly=True,
        copy=False,
        groups="account_credit_control.group_account_credit_control_manager,"
        "account_credit_control.group_account_credit_control_user,"
        "account_credit_control.group_account_credit_control_info",
    )
    credit_control_line_ids = fields.One2many(
        comodel_name="credit.control.line",
        inverse_name="invoice_id",
        string="Credit Lines",
        readonly=True,
        copy=False,
    )

    def button_cancel(self):
        """Prevent to cancel invoice related to credit line"""
        # We will search if this invoice is linked with credit
        cc_line_obj = self.env["credit.control.line"]
        nondraft_domain = [
            ("invoice_id", "in", self.ids),
            ("state", "!=", "draft"),
        ]

        cc_nondraft_lines = cc_line_obj.search(nondraft_domain, limit=1)

        if cc_nondraft_lines:
            raise UserError(
                _(
                    "You cannot cancel this invoice.\n"
                    "A payment reminder has already been "
                    "sent to the customer.\n"
                    "You must create a credit note and "
                    "issue a new invoice."
                )
            )
        draft_domain = [("invoice_id", "in", self.ids), ("state", "=", "draft")]
        cc_draft_line = cc_line_obj.search(draft_domain)
        cc_draft_line.unlink()
        return super().button_cancel()
