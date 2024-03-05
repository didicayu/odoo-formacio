from odoo import models, fields


class PrintPropertyWizard(models.TransientModel):
    _name = "print_property_wizard"
    _description = "print property wizard"

    property_id = fields.Many2one("estate_property", string="Property")

    def print_property(self):
        # Assuming 'report_estate_property_offers' is the external ID of your report action
        report_action = self.env.ref('estate.report_estate_property_offers')

        # Execute the report action for the selected property
        report_data = {'active_id': self.property_id.id}
        return report_action.with_context(**report_data).report_action(
            self.env['estate_property'].browse(self.property_id.id))
