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
    # detailed_type = fields.Selection(
    #     selection=[('game', 'Game'), ('soundtrack', 'Soundtrack'), ('dlc', 'DLC')]
    # )

    # reviews_ids

    @api.depends('release_date')
    def _compute_coming_soon(self):
        for game in self:
            game.coming_soon = (game.release_date > fields.Date.today())
            if game.coming_soon:
                coming_soon_ribbon = self.env['product.ribbon'].search([('html', '=', 'Coming Soon andasjofn')], limit=1)
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

    @api.model
    def debug_ribbons(self):
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


    @api.model
    def create(self, vals):
        new_game = super(VideoGame, self).create(vals)
        new_game.assign_to_upcoming_category()
        return new_game

    def write(self, vals):
        res = super(VideoGame, self).write(vals)
        self.assign_to_upcoming_category()
        return res