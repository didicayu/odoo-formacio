# Copyright 2014-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class FixedFeesTester(common.TransactionCase):
    def setUp(self):
        """Initialize credit control level mock to test fees computations"""
        super().setUp()
        self.currency_model = self.env["res.currency"]
        self.euro = self.env.ref("base.EUR")
        self.assertTrue(self.euro)
        self.usd = self.env.ref("base.USD")
        self.assertTrue(self.usd)

        self.company = self.env["res.company"].create(
            {
                "name": "company_data",
            }
        )
        self.company.currency_id = self.euro
        self.euro_rate = self.env["res.currency.rate"].create(
            {
                "name": "2020-01-01",
                "rate": 0.654,
                "currency_id": self.euro.id,
                "company_id": self.company.id,
            }
        )

        level_obj = self.env["credit.control.policy.level"]
        self.euro_level = level_obj.new(
            {
                "name": "Euro Level",
                "dunning_fixed_amount": 5.0,
                "dunning_currency_id": self.euro,
                "dunning_fees_type": "fixed",
            }
        )

        self.usd_level = level_obj.new(
            {
                "name": "USD Level",
                "dunning_fixed_amount": 5.0,
                "dunning_currency_id": self.usd,
                "dunning_fees_type": "fixed",
            }
        )
        self.dunning_model = self.env["credit.control.dunning.fees.computer"]
        self.line_model = self.env["credit.control.line"]

    def test_type_getter(self):
        """Test that correct compute function is returned for "fixed" type"""
        c_fun = self.dunning_model._get_compute_fun("fixed")
        self.assertEqual(c_fun, self.dunning_model.compute_fixed_fees)

    def test_unknow_type(self):
        """Test that non implemented error is raised if invalide fees type"""
        with self.assertRaises(NotImplementedError):
            self.dunning_model._get_compute_fun("bang")

    def test_computation_same_currency(self):
        """Test that fees are correctly computed with same currency"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": self.euro,
                "company_id": self.company,
            }
        )
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertEqual(fees, self.euro_level.dunning_fixed_amount)

    def test_computation_different_currency(self):
        """Test that fees are correctly computed with different currency"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": self.usd.id,
                "company_id": self.company,
            }
        )
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertAlmostEqual(
            fees, self.euro_level.dunning_fixed_amount / self.euro_rate.rate, 2
        )

    def test_computation_credit_currency_empty(self):
        """Test that fees are correctly computed with empty credit currency"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": False,
                "company_id": self.company,
            }
        )
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertEqual(fees, self.euro_level.dunning_fixed_amount)

    def test_computation_level_currency_empty(self):
        """Test that fees are correctly computed with empty level currency"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": self.euro,
                "company_id": self.company,
            }
        )
        self.euro_level.dunning_currency_id = False
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertEqual(fees, self.euro_level.dunning_fixed_amount)

    def test_computation_all_currency_empty(self):
        """Test that fees are correctly computed with empty currencies"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": False,
                "company_id": self.company,
            }
        )
        self.euro_level.dunning_currency_id = False
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertEqual(fees, self.euro_level.dunning_fixed_amount)

    def test_no_fees(self):
        """Test that fees are not generated if no amount defined on level"""
        credit_line = self.line_model.new(
            {
                "policy_level_id": self.euro_level,
                "currency_id": self.usd,
                "company_id": self.company,
            }
        )
        self.euro_level.dunning_fixed_amount = 0.0
        fees = self.dunning_model.compute_fixed_fees(credit_line)
        self.assertEqual(fees, 0.0)
