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

