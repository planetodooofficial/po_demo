from odoo import api, fields, models, _,tools

class AccessMaster(models.Model):
    _name = 'access.rights.master'

    name = fields.Char('Role')
    right_ids = fields.Many2many('res.groups', string='Groups')