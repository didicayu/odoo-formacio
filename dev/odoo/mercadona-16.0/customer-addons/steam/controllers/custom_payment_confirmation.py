from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtend(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            values = self._prepare_shop_payment_confirmation_values(order)

            # Get the key information for the purchased games
            key_info = []
            for line in order.order_line:
                game_id = line.product_id
                if game_id:
                    partner = request.env.user.partner_id
                    key = partner.acquire_game(game_id.id)
                    key_info.append({
                        'game_name': game_id.name,
                        'key': key
                    })

            # Add the key information to the template context
            values['key_info'] = key_info

            return request.render("website_sale.confirmation", values)
        else:
            return request.redirect('/shop')
