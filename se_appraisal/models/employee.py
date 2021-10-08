from odoo import api, fields, models,_

class Employees(models.Model):
    _inherit = 'hr.employee'

    role = fields.Many2one('role.mapping', "Role")