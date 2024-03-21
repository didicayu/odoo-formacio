from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    games_ids = fields.Many2many('product.product', string="VideoGames")

    is_franchise = fields.Boolean(string='Is Franchise')

    def acquire_game(self, game_id):
        # TODO Add a correct validity date
        # Create a key for the acquired game (linking the key to the game and the current partner)
        Key = self.env['steam.key']
        key_vals = {
            'game_id': game_id,
            'user_id': self.env.user.id
        }
        key = Key.create(key_vals)

        # Add the game to the games_ids field
        self.write({'games_ids': [(4, game_id)]})

        return key.key_code
