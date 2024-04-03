from odoo import models, fields, api
import requests


class FranchiseConfig(models.TransientModel):
    _name = 'franchise.iframe'
    _description = 'Franchise iframe model'
