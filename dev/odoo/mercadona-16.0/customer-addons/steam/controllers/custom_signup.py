from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class CustomAuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        # Extend the request parameters dictionary to include is_franchise
        kw['is_franchise'] = http.request.params.get('is_franchise')

        # Call the original web_auth_signup method
        response = super().web_auth_signup(*args, **kw)

        # Update the is_franchise field for the partner if the user is created successfully
        if 'account_created' in http.request.params:
            # Retrieve the newly created user
            user_login = kw.get('login')
            user = http.request.env['res.users'].sudo().search([('login', '=', user_login)], limit=1)

            # Update the is_franchise field for the partner
            is_franchise = kw.get('is_franchise')
            user.partner_id.write({'is_franchise': is_franchise})

            # Save the updated partner record
            user.partner_id.flush()

        return response

    def get_auth_signup_qcontext(self):
        # Call the original method to get the rendering context
        qcontext = super().get_auth_signup_qcontext()

        # Pass is_franchise parameter to the template
        qcontext['is_franchise'] = http.request.params.get('is_franchise')

        return qcontext

    def _prepare_signup_values(self, qcontext):
        # Call the original method to prepare signup values
        values = super()._prepare_signup_values(qcontext)

        # Include is_franchise parameter
        values['is_franchise'] = qcontext.get('is_franchise')

        return values
