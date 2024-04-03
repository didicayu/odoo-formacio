from odoo import models, fields


class CustomBase(models.Model):
    _name = "custom.base"
    original_id = fields.Integer()


class ProductProduct(models.Model):
    # _inherit = ["product.product", "custom.base"]
    _inherit = "product.product"
    original_id = fields.Integer()


class ProductTemplate(models.Model):
    # _inherit = ["product.template", "custom.base"]
    _inherit = "product.template"
    original_id = fields.Integer()
