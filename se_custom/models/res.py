from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    _sql_constraints = [
        ('code_company_uniq', 'unique (name)',
         'Company already exist with same name')
    ]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_currency_id = fields.Many2one('res.currency',string="Partner Currency",default=lambda self: self.env.company.currency_id)
