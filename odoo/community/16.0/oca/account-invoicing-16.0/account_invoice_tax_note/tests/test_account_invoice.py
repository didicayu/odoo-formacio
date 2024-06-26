# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAccountInvoice(TransactionCase):
    """
    Tests for account.invoice
    """

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        tax_group_obj = self.env["account.tax.group"]
        tax_obj = self.env["account.tax"]
        invoice_obj = self.env["account.move"]
        self.product1 = self.env.ref("product.product_product_7")
        self.product2 = self.env.ref("product.product_product_8")
        customer = self.env.ref("base.res_partner_2")
        self.tax_group1 = tax_group_obj.create(
            {"name": "Secret Taxes", "sequence": 20, "report_note": str(uuid4())}
        )
        self.tax_group2 = tax_group_obj.create(
            {"name": "Public taxes", "sequence": 30, "report_note": str(uuid4())}
        )
        self.tax1 = tax_obj.create(
            {
                "name": "TVA 1",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": "35",
                "description": "Top secret",
                "tax_group_id": self.tax_group1.id,
            }
        )
        self.tax2 = tax_obj.create(
            {
                "name": "TVA 2",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": "22",
                "description": "Hello",
                "tax_group_id": self.tax_group2.id,
            }
        )
        taxes = self.tax1 | self.tax2
        self.product1.write({"taxes_id": [(6, False, self.tax1.ids)]})
        self.product2.write({"taxes_id": [(6, False, self.tax2.ids)]})
        account = self.env["account.account"].search(
            [("account_type", "=", "income")], limit=1
        )
        account.write({"tax_ids": [(4, self.tax1.id, False), (4, self.tax2.id, False)]})
        journal = self.env["account.journal"].create(
            {"name": "Sale journal - Test", "code": "SJ-TT", "type": "sale"}
        )
        invoice_lines1 = [
            (
                0,
                False,
                {
                    "name": self.product1.display_name,
                    "product_id": self.product1.id,
                    "quantity": 3,
                    "product_uom_id": self.product1.uom_id.id,
                    "price_unit": self.product1.standard_price,
                    "account_id": account.id,
                    "tax_ids": self.tax1.ids,
                },
            )
        ]
        # Invoice 1 must have 1 tax group only
        self.invoice1 = invoice_obj.create(
            {
                "partner_id": customer.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines1,
                "invoice_origin": "Unit test",
                "journal_id": journal.id,
            }
        )
        invoice_lines2 = [
            (
                0,
                False,
                {
                    "name": self.product1.display_name,
                    "product_id": self.product1.id,
                    "quantity": 3,
                    "product_uom_id": self.product1.uom_id.id,
                    "price_unit": self.product1.standard_price,
                    "account_id": account.id,
                    "tax_ids": self.tax1.ids,
                },
            ),
            (
                0,
                False,
                {
                    "name": self.product1.display_name,
                    "product_id": self.product2.id,
                    "quantity": 3,
                    "product_uom_id": self.product2.uom_id.id,
                    "price_unit": self.product2.standard_price,
                    "account_id": account.id,
                    "tax_ids": taxes.ids,
                },
            ),
        ]
        # Invoice 2 must have more than 1 tax group
        self.invoice2 = invoice_obj.create(
            {
                "partner_id": customer.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines2,
                "invoice_origin": "Unit test",
                "journal_id": journal.id,
            }
        )

    def test_get_account_tax_groups_with_notes1(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use an invoice with only 1 tax group
        :return: bool
        """
        tax_group = self.invoice1.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need only 1 tax group for this test
        self.assertEqual(len(tax_group), 1)
        tax_group_result = self.invoice1._get_account_tax_groups_with_notes()
        self.assertEqual(set(tax_group.ids), set(tax_group_result.ids))
        return True

    def test_get_account_tax_groups_with_notes2(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use an invoice with more than 1 tax group
        :return: bool
        """
        tax_group = self.invoice2.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need more than 1 tax group for this test
        self.assertGreater(len(tax_group), 1)
        tax_group_result = self.invoice2._get_account_tax_groups_with_notes()
        self.assertEqual(set(tax_group.ids), set(tax_group_result.ids))
        return True

    def test_get_account_tax_groups_with_notes3(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use the function on a multi invoice without any
        taxes. So the result should be empty
        :return: bool
        """
        self.invoice1.invoice_line_ids.write({"tax_ids": [(6, False, [])]})
        tax_group = self.invoice1.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need 0 tax group for this test
        self.assertFalse(bool(tax_group))
        tax_group_result = self.invoice1._get_account_tax_groups_with_notes()
        self.assertFalse(bool(tax_group_result))
        return True
