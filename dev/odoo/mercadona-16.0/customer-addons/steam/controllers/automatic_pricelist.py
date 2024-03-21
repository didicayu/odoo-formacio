from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSaleOriginal


class WebsiteSale(WebsiteSaleOriginal):

    def sitemap_shop(self):
        return super(WebsiteSale, self).sitemap_shop

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        # Call the original shop method
        response = super(WebsiteSale, self).shop(page, category, search, min_price, max_price, ppg, **post)

        # Custom logic to set the price list based on the user's franchise status
        self._set_pricelist_for_user()

        self._set_product_visibility(response)

        return response

    def _set_product_visibility(self, response):
        # Fetch products based on visibility settings
        products = request.env['product.template'].search([
            ('website_published', '=', True),  # Only published products
            ('visibility', 'in', ['everyone', 'franchise'])  # Visible to everyone or franchise
        ])

        # If the user is not a franchise, filter out franchise-only products
        user = request.env.user
        if not user.partner_id.is_franchise:
            products = products.filtered(lambda p: p.visibility != 'franchise')

        # Update the response with filtered products
        response.qcontext['products'] = products

    def _set_pricelist_for_user(self):
        user = request.env.user
        is_franchise = user.partner_id.is_franchise if user.partner_id else False
        pricelist_id = self._get_custom_pricelist_id(is_franchise)
        request.session['website_sale_current_pl'] = pricelist_id

    def _get_custom_pricelist_id(self, is_franchise):
        pricelist_model = request.env['product.pricelist']
        if is_franchise:
            b2b_pricelist = pricelist_model.search([('name', '=', 'B2B')], limit=1)
            return b2b_pricelist.id if b2b_pricelist else False
        else:
            b2c_pricelist = pricelist_model.search([('name', '=', 'B2C')], limit=1)
            return b2c_pricelist.id if b2c_pricelist else False

