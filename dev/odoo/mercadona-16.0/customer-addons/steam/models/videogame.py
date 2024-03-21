from odoo import fields, models, api


class VideoGame(models.Model):
    _inherit = "product.template"

    release_date = fields.Date(copy=False, required=True, default=fields.date.today())
    coming_soon = fields.Boolean(copy=False, compute='_compute_coming_soon', store=True)
    developer = fields.Char(required=True, copy=False, default="Unknown Developer Inc.")
    pegi_rating = fields.Selection(
        string="PEGI Rating",
        selection=[('3', 'PEGI 3'), ('7', 'PEGI 7'), ('12', 'PEGI 12'), ('16', 'PEGI 16'), ('18', 'PEGI 18')],
        default='3',
        required=True
    )

    game_tag_ids = fields.Many2many('steam.tag', string="Game Tags")
    language_ids = fields.Many2many('steam.language', string='Available Languages')

    key_ids = fields.One2many("steam.key", "game_id", string="Product Keys", readonly=True)

    visibility = fields.Selection([
        ('everyone', 'Everyone'),
        ('franchise', 'Franchise Only'),
        ('admin', 'Admin Only')
    ], default='everyone', string='Visibility')

    @api.depends('release_date')
    def _compute_coming_soon(self):
        for game in self:
            game.coming_soon = (game.release_date > fields.Date.today())
            self._check_coming_soon_ribbon(game)

            # Publish the game if the release date has been reached
            game.website_published = not game.coming_soon

    def _check_coming_soon_ribbon(self, game):
        coming_soon_ribbon = self.env['product.ribbon'].search([('html', '=', 'Coming Soon')], limit=1)

        if game.coming_soon:
            if coming_soon_ribbon:
                game.website_ribbon_id = coming_soon_ribbon.id
            else:
                coming_soon_ribbon_values = {
                    'html': 'Coming Soon',  # Adjust HTML as needed
                    'html_class': 'o_ribbon_left',
                    'bg_color': 'rgb(230, 46, 0)',  # Adjust color as needed
                    'text_color': 'rgb(255, 255, 255)',  # Adjust color as needed
                }
                ribbon = self.env['product.ribbon'].create(coming_soon_ribbon_values)
                game.website_ribbon_id = ribbon.id

        else:
            game.website_ribbon_id = False

    @api.model
    def _debug_ribbons(self):
        ribbons = self.env['product.ribbon'].search([])
        for ribbon in ribbons:
            print(f"Ribbon ID: {ribbon.id}")
            print(f"HTML: {ribbon.html}")
            print(f"Background Color: {ribbon.bg_color}")
            print(f"Text Color: {ribbon.text_color}")
            print(f"HTML Class: {ribbon.html_class}")
            print("---------------------------")

    def assign_to_upcoming_category(self):
        upcoming_category = self.env['product.public.category'].search([('name', '=', 'Upcoming releases')], limit=1)
        if not upcoming_category:
            # Create the category if it doesn't exist
            upcoming_category = self.env['product.public.category'].create({'name': 'Upcoming releases'})

        upcoming_games = self.filtered(lambda g: g.coming_soon and upcoming_category not in g.public_categ_ids)
        if upcoming_games:
            upcoming_games.write({'public_categ_ids': [(4, upcoming_category.id)]})

    def assign_pos_category(self):
        new_releases_category = self.env['pos.category'].search([('name', '=', 'New Releases')], limit=1)
        if not new_releases_category:
            # Create the category if it doesn't exist
            new_releases_category = self.env['pos.category'].create({'name': 'New Releases'})

        # Filter the games that are coming soon and not yet assigned to the New Releases category
        upcoming_games = self.search([('coming_soon', '=', True), ('pos_categ_id', '!=', new_releases_category.id)])

        if upcoming_games:
            # Update the pos_categ_id for the filtered games
            upcoming_games.write({'pos_categ_id': new_releases_category.id})

        # TODO fix what happens when a game is no longer coming_soon



    @api.model
    def create(self, vals):
        # Set available_in_pos to True when creating a new VideoGame
        vals['available_in_pos'] = True
        new_game = super(VideoGame, self).create(vals)
        new_game.assign_to_upcoming_category()
        new_game.assign_pos_category()
        return new_game

    def write(self, vals):
        # Set available_in_pos to True when updating an existing VideoGame
        if 'available_in_pos' not in vals:
            vals['available_in_pos'] = True
        res = super(VideoGame, self).write(vals)
        self.assign_to_upcoming_category()
        self.assign_pos_category()
        return res
