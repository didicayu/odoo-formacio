from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = ['project.project', 'image.mixin']
    _name = 'project.project'
    _description = 'Project Image'

    show_image = fields.Boolean(string="Show Image", default=True, group='project_image.group_project_image')
    image_1920 = fields.Image("Image")
