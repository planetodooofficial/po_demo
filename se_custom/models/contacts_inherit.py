from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError


class Contacts(models.Model):
    _inherit = 'res.partner'

    msme = fields.Char("MSME")
    partner_code = fields.Char("Partner Code")

    _sql_constraints = [
        ('code_contact_uniq', 'unique (name)',
         'Contact already exist with same name')
    ]

    # @api.constrains('name')
    # def _check_reconcile(self):
    #     partners = self.env['res.partner'].search([('name','=',self.name),('id','!=',self.id)])
    #     if partners:
    #         raise ValidationError(_('Contact already exist with same name !'))















