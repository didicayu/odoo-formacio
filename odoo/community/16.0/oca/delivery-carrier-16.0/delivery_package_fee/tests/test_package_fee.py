# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase
from odoo.tools import mute_logger


class TestPackageFee(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product", "lst_price": 1.0}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product", "lst_price": 1.0}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        cls.carrier_product = cls.env["product.product"].create(
            {"name": "Shipping", "type": "service"}
        )
        cls.fee1 = cls.env["product.product"].create(
            {"name": "LSVA Fee", "type": "service", "lst_price": 3.0}
        )
        cls.fee2 = cls.env["product.product"].create(
            {"name": "Service Fee", "type": "service", "lst_price": 4.0}
        )

        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Delivery",
                "fixed_price": 10.0,
                "product_id": cls.carrier_product.id,
                "package_fee_ids": [
                    (0, 0, {"product_id": cls.fee1.id}),
                    (0, 0, {"product_id": cls.fee2.id}),
                ],
            }
        )
        cls.wh = cls.env.ref("stock.warehouse0")

        cls.sale = cls._create_sale()
        cls._add_sale_carrier(cls.sale, cls.carrier)
        cls._update_qty_in_location(
            cls.wh.lot_stock_id,
            cls.sale.order_line[0].product_id,
            cls.sale.order_line[0].product_uom_qty,
        )
        cls._update_qty_in_location(
            cls.wh.lot_stock_id,
            cls.sale.order_line[1].product_id,
            cls.sale.order_line[1].product_uom_qty,
        )
        cls.sale.action_confirm()

        cls.pack1 = cls.env["stock.quant.package"].create({})
        cls.pack2 = cls.env["stock.quant.package"].create({})

        cls.sptype1 = cls.env["stock.package.type"].create({"name": "SPType 1"})
        cls.sptype2 = cls.env["stock.package.type"].create({"name": "SPType 2"})

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        quants = cls.env["stock.quant"]._gather(product, location, strict=True)
        # this method adds the quantity to the current quantity, so get the diff
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    @classmethod
    def _create_sale(cls):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with mute_logger("odoo.tests.common.onchange"):
            with sale_form.order_line.new() as line:
                line.product_id = cls.product1
                line.product_uom_qty = 10.0
            with sale_form.order_line.new() as line:
                line.product_id = cls.product2
                line.product_uom_qty = 10.0
        return sale_form.save()

    @classmethod
    def _add_sale_carrier(cls, sale, carrier):
        delivery_wizard = Form(
            cls.env["choose.delivery.carrier"].with_context(
                default_order_id=sale.id, default_carrier_id=carrier.id
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    def test_package_fee_simple(self):
        """All stock moves processed at once"""
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    # one unit per package
                    "product_uom_qty": 2.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 2.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(picking.name),
                },
            ],
        )

    def test_package_fee_simple_with_fiscal_position_tax(self):
        """All stock moves processed at once"""

        # Creating taxes and fiscal position
        tax_price_include = self.env["account.tax"].create(
            {
                "name": "10% inc",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10,
                "price_include": True,
                "include_base_amount": True,
            }
        )
        tax_price_exclude = self.env["account.tax"].create(
            {
                "name": "15% exc",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 15,
            }
        )

        fiscal_position = self.env["account.fiscal.position"].create(
            {
                "name": "fiscal_pos_a",
                "tax_ids": [
                    (
                        0,
                        None,
                        {
                            "tax_src_id": tax_price_include.id,
                            "tax_dest_id": tax_price_exclude.id,
                        },
                    ),
                ],
            }
        )

        # Setting tax in fiscal position on fee2 product
        self.fee2.taxes_id = tax_price_include
        self.sale.fiscal_position_id = fiscal_position

        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        so_line_fee1 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.fee1
        )
        so_line_fee2 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.fee2
        )

        self.assertNotEqual(so_line_fee1.tax_id[0], tax_price_exclude)
        # only fee2 has tax tax_price_exclude due to defined fiscal position
        self.assertEqual(so_line_fee2.tax_id[0], tax_price_exclude)

    def test_package_fee_backorder(self):
        """Stock moves valided in 2 times using a backorder"""
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")
        backorder = picking.backorder_ids

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(picking.name),
                },
            ],
        )

        backorder.move_line_ids[0].result_package_id = self.pack2
        backorder.move_line_ids[0].qty_done = 10.0
        backorder._action_done()
        self.assertEqual(backorder.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # these lines have been added by the first picking
                {
                    "product_id": self.fee1.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(picking.name),
                },
                # new lines added for the backorder
                {
                    "product_id": self.fee1.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(backorder.name),
                },
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 1.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(backorder.name),
                },
            ],
        )

    def test_package_fee_pricelist(self):
        """Price set on a pricelist is used"""
        # set pricelist prices for package fees
        pricelist = self.sale.pricelist_id
        fee1_price = 13.5
        fee2_price = 17.2
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist.id,
                "product_id": self.fee1.id,
                "applied_on": "0_product_variant",
                "fixed_price": fee1_price,
            }
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist.id,
                "product_id": self.fee2.id,
                "applied_on": "0_product_variant",
                "fixed_price": fee2_price,
            }
        )

        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    # one unit per package
                    "product_uom_qty": 2.0,
                    "price_unit": fee1_price,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 2.0,
                    "price_unit": fee2_price,
                    "name": "Service Fee ({})".format(picking.name),
                },
            ],
        )

    def test_package_no_package(self):
        """No packages, no fees"""
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].qty_done = 10.0
        picking.with_context(set_default_package=False)._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
            ],
        )

    def test_package_no_price(self):
        """No price on product, no fees"""
        picking = self.sale.picking_ids
        self.fee1.lst_price = 0.0
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # only the Service Fees are added because there is
                # no price on the LSVA (could be free for a customer
                # based on a pricelist for instance)
                {
                    "product_id": self.fee2.id,
                    # one unit per package
                    "product_uom_qty": 2.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(picking.name),
                },
            ],
        )

    def test_package_with_type_no_fee_line(self):
        """Assign all fee lines to a package type, no fee line added to SO"""
        self.carrier.package_fee_ids.write({"package_type_id": self.sptype1.id})
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
            ],
        )

    def test_package_with_type_one_fee_line(self):
        """Assign all fee lines to a package type, but one fee line added to SO"""
        self.carrier.package_fee_ids[0].package_type_id = self.sptype1
        self.carrier.package_fee_ids[1].package_type_id = self.sptype2
        self.pack1.package_type_id = self.sptype1
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
            ],
        )

    def test_package_with_type_one_fee_line_qty(self):
        """Assign all fee lines to a package type, but one fee line added to SO, qty=2"""
        self.carrier.package_fee_ids[0].package_type_id = self.sptype1
        self.carrier.package_fee_ids[1].package_type_id = self.sptype2
        self.pack1.package_type_id = self.sptype1
        self.pack2.package_type_id = self.sptype1
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    "product_uom_qty": 2.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
            ],
        )

    def test_package_with_type_two_fee_line_qty(self):
        """Assign all fee lines to a package type, 2 fee lines added to SO"""
        self.carrier.package_fee_ids[0].package_type_id = self.sptype1
        self.carrier.package_fee_ids[1].package_type_id = self.sptype2
        self.pack1.package_type_id = self.sptype1
        self.pack2.package_type_id = self.sptype2
        picking = self.sale.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].result_package_id = self.pack1
        picking.move_line_ids[0].qty_done = 10.0
        picking.move_line_ids[1].result_package_id = self.pack2
        picking.move_line_ids[1].qty_done = 10.0
        picking._action_done()
        self.assertEqual(picking.state, "done")

        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 1",
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_qty": 10.0,
                    "price_unit": 1.0,
                    "name": "Product 2",
                },
                {
                    "product_id": self.carrier_product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 10.0,
                    "name": "Delivery",
                },
                # additional package fee lines from here
                {
                    "product_id": self.fee1.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 3.0,
                    "name": "LSVA Fee ({})".format(picking.name),
                },
                {
                    "product_id": self.fee2.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 4.0,
                    "name": "Service Fee ({})".format(picking.name),
                },
            ],
        )
