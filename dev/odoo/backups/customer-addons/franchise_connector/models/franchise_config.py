from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


class FranchiseConfig(models.TransientModel):
    _name = 'franchise.config'
    _inherit = ['franchise.data.fetch.mixin']
    _description = 'Franchise Configuration'

    franchise_username = fields.Char(string='Franchise Username', required=True)
    franchise_password = fields.Char(string='Password', required=True)
    central_db = fields.Char(string='Central Database', required=True, default='mercadona-v16.0-dev')
    central_system_url = fields.Char(string='Central System URL', required=True, default='http://localhost:8080')
    api_key = fields.Char(string='API Key', required=True, store=True)
    connection_success = fields.Boolean(string='Connection Successful', readonly=True)

    def test_connection(self):
        self.ensure_one()
        url = self.central_system_url
        api_key = self.api_key
        try:
            # Make a test API request to the central system
            response = requests.get(url, headers={'Authorization': f'Bearer {api_key}'})
            # Set flag based on the response status
            self.connection_success = response.ok
            # Return a dictionary with message details
            return {
                'name': 'Connection Test',
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test',
                    'type': 'success' if response.ok else 'warning',
                    'message': 'Connection successful' if response.ok else 'Connection failed',
                }
            }
        except requests.exceptions.RequestException as e:
            # Handle connection errors
            raise UserError(f"Connection failed: {e}")

    def save_configuration(self):
        self.ensure_one()
        # Update the current record with the values entered by the user
        self.write({
            'franchise_username': self.franchise_username,
            'franchise_password': self.franchise_password,
            'central_db': self.central_db,
            'central_system_url': self.central_system_url,
            'api_key': self.api_key,
        })

        record_models = ['product.template', 'product.product']
        self.set_auth_data(self.central_db, self.franchise_username, self.franchise_password, self.central_system_url, self.api_key)
        self.synchronize_models(record_models)

        # Return a dictionary to close the wizard
        return {'type': 'ir.actions.act_window_close'}