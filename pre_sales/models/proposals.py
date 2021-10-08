from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
from datetime import date
from datetime import timedelta
import base64
from num2words import num2words


class ProposalMethods(models.Model):
    _inherit = 'sale.order'

    pro_posals = fields.Selection(
        [('techno_comm', 'Techno-commercial proposal'), ('technical_prop', 'Technical proposal'),
         ('commercial_prop', 'Commercial proposal')], string="Proposal Types", default="techno_comm")
    sale_work_id = fields.One2many('sale.finance', 'sale_fin_id')
    methodology_document = fields.Many2one('hr.document', string='Methodologies',
                                           domain="[('types_doc', '=', 'methodology')]")

    def send_proposals(self):
        collect = self.version
        self.check_proposal = True
        if self.count == 1:
            self.count += 1
        else:
            convert = 'V' + str(int(collect.replace('V', '')) + 1)
            self.version = convert
        template_id = self.env['ir.model.data'].xmlid_to_res_id('pre_sales.email_proposals_send',
                                                                raise_if_not_found=False)
        data_ids = []
        for rec in self.assign_many_proposal:
            report_template_id = self.env.ref(rec.xml_id)._render_qweb_pdf(self.id)
            if report_template_id:
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name':rec.name,
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                }
                data_ids.extend(self.env['ir.attachment'].create(ir_values).ids)
        if self.methodology_document:
            methodology_document_ids = self.methodology_document.mapped('attach_id').ids
            data_ids.extend(methodology_document_ids)
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6, 0, data_ids)]
        ctx = {
            'default_model': 'sale.order',
            'default_template_id': template.id,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class Financials(models.Model):
    _name = 'sale.finance'

    description_work = fields.Char(string="Description of Work")
    amount_inr = fields.Float(string="Amount in INR")
    amount_gst = fields.Float(string="GST @ 18%")
    amount_total = fields.Float(string="Total Amount in INR")
    sale_fin_id = fields.Many2one('sale.order')
    amount_words = fields.Char('In words')

    @api.onchange('amount_inr')
    def onchange_amount(self):
        for line in self:
            line.amount_gst = line.amount_inr * 0.18
            line.amount_total = line.amount_gst + line.amount_inr
            line.amount_words = num2words(line.amount_total, lang='en_IN').replace(',', '')

class ProducttemplatesInherit(models.Model):
    _inherit = 'product.template'

    @api.constrains('product_code')
    def _validate_product_code_template_category(self):
        for prod in self:
            product_code_search = self.env['product.template'].search([
                ('product_code', '=', prod.product_code),('id','!=',prod.id)])
            if product_code_search:
                raise ValidationError(_("Product code must be unique"))

class ProductproductInherit(models.Model):
    _inherit = 'product.product'

    @api.constrains('product_code')
    def _validate_product_code_product_category(self):
        for prod in self:
            product_code_search = self.env['product.product'].search([
                ('product_code', '=', prod.product_code),('id','!=',prod.id)])
            if product_code_search:
                raise ValidationError(_("Product code must be unique"))


class PartnerResInherit(models.Model):
    _inherit = 'res.partner'

    @api.constrains('partner_code')
    def _validate_partner_code_customer(self):
        for part_ner in self:
            partner_code_search = self.env['res.partner'].search([
                ('partner_code', '=', part_ner.partner_code),('id','!=',part_ner.id)])
            if partner_code_search:
                raise ValidationError(_("Partner code must be unique"))

