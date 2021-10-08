from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _inherit = 'product.template'

    department = fields.Many2one('hr.department',"Department")
    product_code = fields.Char("Product Code")

    @api.constrains('name')
    def _check_product_name(self):
        products = self.env['product.template'].search([('name', '=', self.name), ('id', '!=', self.id)])
        if products:
            raise ValidationError(
                _('Product already exist with same name !'))
