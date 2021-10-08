from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
import datetime
from PyPDF2 import PdfFileMerger


class SaleQuestionare(models.Model):
    _inherit = 'sale.order'

    questionare_document = fields.Many2many('hr.document', string='Questionaire',domain="[('types_doc', '=', 'questionare')]" )
    demo = fields.Char(string='Demo')

    def send_questionaire(self):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('pre_sales.email_questionaire_send',
                                                                raise_if_not_found=False)
        print('template_id', template_id)
        self.check_proposal = False
        template = self.env['mail.template'].browse(template_id)
        if self.questionare_document:
            questionare_document_ids = self.questionare_document.mapped('attach_id').ids
            print('questionare_document_ids', questionare_document_ids)
            template.attachment_ids = [(6, 0, questionare_document_ids)]
            print('template', template.attachment_ids)
            ctx = {
                'default_model': 'sale.order',
                'default_template_id': template.id,
                'force_email': True,
            }
        else:
            template.attachment_ids =False
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

    def alert_reminder_questionaire(self):
        check_projects = self.project_ids
        self.check_proposal = False
        print(check_projects)
        template_id = self.env['ir.model.data'].xmlid_to_res_id('pre_sales.alert_questionaire_send',
                                                                raise_if_not_found=False)
        ctx = {
            'default_model': 'sale.order',
            'default_template_id': template_id,
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

    # def action_confirm(self):
    #     res = super(SaleQuestionare, self).action_confirm()
    #     if self.project_ids:
    #         for projects in self.project_ids:
    #             if projects.user_id and projects.user_id and self.partner_id.mobile or self.partner_id.phone:
    #                 message = """
    #                                                              <p>Dear """ + projects.user_id.name + """</p>
    #                                                              <p>New Sale Order  of """ + self.partner_id.name + """ with contact details """ + str(self.partner_id.phone) + """</p>
    #                                                              <br/>
    #
    #                                                                                          """
    #                 email_vals = {
    #                     'subject': """New Sale Order is created""",
    #                     'email_to': projects.user_id.login ,
    #                     'body_html': message,
    #                 }
    #                 email = self.env['mail.mail'].sudo().create(email_vals)
    #                 email.sudo().send()
    #
    #     return res

class ResConfigSettingsPreSales(models.TransientModel):
    _inherit = 'res.config.settings'

    alert_id = fields.Char(string="Sales Alert Mail Id")

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsPreSales, self).get_values()
        res.update(
            alert_id=self.env['ir.config_parameter'].sudo().get_param(
                'pre_sales.alert_id'),
        )
        return res

    def set_values(self):
        super(ResConfigSettingsPreSales, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.alert_id or False

        param.set_param('pre_sales.alert_id', field1)


