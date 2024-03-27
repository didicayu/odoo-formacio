from odoo import models, fields
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = ['res.partner', 'api.key.user.mixin']
    _name = 'res.partner'

    games_ids = fields.Many2many('product.product', string="VideoGames")

    is_franchise = fields.Boolean(string='Is Franchise')
    is_approved = fields.Boolean(string="Is approved", default=False)

    api_key_ids = fields.One2many('res.users.apikeys', string="Partner API Keys",
                                  compute='_compute_partner_apikeys_ids')

    def _compute_partner_apikeys_ids(self):
        """Gets the api keys related to the partner"""
        for partner in self:
            user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
            partner.api_key_ids = user.api_key_ids

    def acquire_game(self, game_id):
        # TODO Add a correct validity date other than the default +10 years
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

    def approve_partner(self):
        """Method to approve the partner and create a user."""
        for partner in self:
            if partner.is_franchise:

                # FIXME el proceso de registro crea usuarios de manera automatica, no hace falta crear nuevos en un
                #  principio

                # # Create a user linked to the partner
                # user_vals = {
                #     'name': partner.name,
                #     'login': partner.email or partner.phone or '',  # Use email or phone as login if available
                #     'partner_id': partner.id,
                #     'is_company': True,
                #     # Add other user fields as needed
                # }
                # user = self.env['res.users'].create(user_vals)
                #
                # print("User created:", user.name, user.login, user.partner_id.name)

                # Generate API key related to the user we are about to approve
                user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                k = self.generate_api_key(None, 'test key', user.id)

                # Get the email address of the user
                user = self.env['res.users'].browse(user.id)
                email = user.partner_id.email

                # Send the API key by email
                template = self.env.ref('steam.email_template_api_key')
                template.send_mail(user.id, force_send=True)
                print(f'Email sent to user with API key')

                # Set the partner as approved
                partner.is_approved = True

            else:
                raise UserError("Only franchise partners can be approved.")

    def write(self, vals):
        return super().write(vals)
