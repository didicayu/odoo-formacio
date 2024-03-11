from odoo import models, fields, api


class GameLanguage(models.Model):
    _name = 'steam.language'
    _description = 'Available Languages for Games'

    name = fields.Char(string='Language', required=True)
    interface_support = fields.Boolean(string='Interface Support')
    audio_support = fields.Boolean(string='Full Audio Support')
    subtitle_support = fields.Boolean(string='Subtitle Support')
