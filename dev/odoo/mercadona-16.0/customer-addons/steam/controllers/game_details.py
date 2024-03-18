from odoo import http
from odoo.http import request

class GameDetailsController(http.Controller):

    @http.route('/game-details/<int:game_id>', type='http', auth='public', website=True)
    def game_details_page(self, game_id):
        game = request.env['product.product'].browse(game_id)
        keys = request.env['steam.key'].search([('game_id', '=', game_id)])

        return http.request.render('steam.game_details_template', {'game': game, 'keys': keys})
