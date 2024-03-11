from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    games_ids = fields.Many2many('product.product', string='VideoGames')

    def write(self, vals):

        # FIXME Aquest codi serveix per generar claus quan s'assigna un joc nou a un jugador,
        #  pero no s'entra dins de la for-loop

        # Original write method
        res = super(Users, self).write(vals)

        if 'games_ids' in vals:

            added_games = self.games_ids - self._origin.games_ids
            print("Added Games: ", added_games)
            for game in added_games:
                key_values = {
                    'game_id': game.id,
                    'user_id': self.id,
                }
                self.env['steam.key'].create(key_values)

        return res
