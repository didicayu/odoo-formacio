from odoo import http
from odoo.http import request


class GameController(http.Controller):

    @http.route('/library', type='http', auth='user', website=True)
    def library_page(self):
        partner = request.env.user.partner_id
        games = partner.games_ids
        print(games)
        return http.request.render('steam.library_template', {'partner': partner, 'games': games})
