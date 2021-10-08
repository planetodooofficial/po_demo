import base64
import ast

from odoo.exceptions import UserError
from odoo.http import request

from odoo import api, fields, models, _




class OfferLetterDetails(models.Model):
    _name = 'offer.letter'
    _rec_name = 'cand_name'

    cand_name = fields.Many2one('hr.applicant',string='Canditate Name',required=True)
    poss_tion = fields.Char(string="Position")
    job_id = fields.Many2one('hr.job', "Job Position", domain="[('state', '!=', 'new')]",required=True)
    is_approve_cand = fields.Boolean("Is Approve",default=False)
    is_reject_offer = fields.Boolean("Is Rejected offer",default=False)
    date_of_join = fields.Date(string="Date of Joining",required=True)
    ctcs = fields.Integer(string="Ctc",required=True)
    # ctcs_mon = fields.Monetary(string="Ctc",required=True)
    job_location = fields.Char(string="Job location",required=True)
    state = fields.Selection([
        ('new', 'Draft'), ('approved', 'Approved')], string='Status', readonly=True, default='new',
        help="Whether its approved by Hod or not")
    country_id = fields.Many2one('res.country', string='Country', )
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]",required=True)
    state_code = fields.Char(related='state_id.code',required=True)
    city = fields.Char('City',required=True)
    zip = fields.Char('ZIP',required=True)
    street = fields.Char('Street',required=True)
    street2 = fields.Char('Street2',required=True)
    trans_allow_annuals=fields.Integer(string="Transport Allowance (annual)",default=19200,required=True)
    medical_allow_annuals=fields.Integer(string="Medical Allowance (annual)",default=15000,required=True)
    statutory_bonus_annuals=fields.Integer(string="Statutory Bonus (annual)",default=19200,required=True)
    plb_annuals=fields.Integer(string="PLB* annual",required=True)
    pf_annuals=fields.Integer(string="PF Employer Contribution (annual)",default=21600,required=True)
    certi_allows=fields.Integer(string="Certification Allowance**")
    medical_allows=fields.Integer(string="Medical Insurance***",default=15000,required=True)
    join_in_bonus=fields.Integer(string="Joining Bonus")
    clause = fields.Text(string="Joining Bonus Note")
    reject_reason_offer = fields.Text(string="Rejection Reason")


    def approval_need(self):
        report_template_id = self.env.ref('se_hr.action_offer_letter_receipt')._render_qweb_pdf(self.id)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Offer Letter",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        users = self.env['res.users'].search([])
        for auth_user in users:
            if auth_user.has_group('se_hr.group_HR_hod_user'):
                base_url = request.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
                url_approve = self.get_base_url() + '/approve_hod/' + str(self.id)
                message = """
                                                         <p>Dear """ + auth_user.name + """</p>
                                                         <p>Kindly approve the offer letter of """ + self.cand_name.name + """ .please find below attachment for Offer letter details</p>
                                                         <button style="background-color:#875A7B;color:white; padding:5px; font-size:16px;">
                                        <a style="color:white; text-decoration:none;" href='""" + base_url + """'> Approve/Reject</a></button>
                                                         <br/>

                                                                                     """
                email_vals = {
                    'subject': """Offer Letter Approval Request""",
                    'email_to': "shivani.planetodoo@gmail.com",
                    'body_html': message,
                    'attachment_ids': [(6, 0, data_id.ids)]

                }
                email = self.env['mail.mail'].sudo().create(email_vals)
                email.sudo().send()


    def approval_need_from_hod(self):
        self.write({'state': 'approved'})

    def reject_by_hod(self):
        self.write({'state': 'new'})
        self.is_reject_offer=True
        self.write({'state': 'new'})

    @api.model
    def create(self, vals):
        res = super(OfferLetterDetails, self).create(vals)
        print(res.id)
        res.cand_name.offer_letter_appl = res.id
        stage = self.env['hr.recruitment.stage'].search([('name', '=', "Offer Checker")], limit=1)
        res.cand_name.stage_id = stage.id
        # res.cand_name.is_offer = True
        # res.cand_name.offer_letter_counts = 1
        return res

    def send_candidate(self):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('se_hr.email_offer_letter_approval',
                                                                raise_if_not_found=False)
        ctx = {
            'default_model': 'offer.letter',
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

class EmailCompose(models.TransientModel):
    _inherit = 'mail.compose.message'

    emailto = fields.Char(string="Email To")

    def action_send_mail(self):
        res=super(EmailCompose, self).action_send_mail()
        active_model=self.env.context.get('active_model') == 'offer.letter'
        active_id = self._context.get('active_id')
        if self.env.context.get('active_model') == 'offer.letter' and active_id:
            email_pass=self.env['offer.letter'].search([('id', '=', active_id)])
            print(email_pass)
            url_approve = self.get_base_url() + '/approve/' + str(active_id)
            message = """
                                                <div style="margin: 0px; padding: 0px;">
                                                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                                        Dear """ + email_pass.cand_name.partner_name + """ ,<br/>Your Offer Letter Has been generated please find the
                                                        attachment
                                                        <br/>
                                                        <br/>
                                                    </p>
                                                    <div class="col">
                                                        <a href=""" + url_approve + """
                                                           target="_blank"
                                                           style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
                                                            Accept
                                                        </a>
                                                    </div>
                                                </div>

                                                                                                 """
            email_vals = {
                'subject': """Offer Letter Approval Request""",
                'body_html': message,
                'email_to': self.emailto,
                'attachment_ids': [(6, 0, self.attachment_ids.ids)]

            }
            email = self.env['mail.mail'].sudo().create(email_vals)
            email.sudo().send()

            pass

    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        notif_layout = self._context.get('custom_layout')
        # Several custom layouts make use of the model description at rendering, e.g. in the
        # 'View <document>' button. Some models are used for different business concepts, such as
        # 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
        # different wording depending on the state of the object.
        # Therefore, we can set the description in the context from the beginning to avoid falling
        # back on the regular display_name retrieved in '_notify_prepare_template_context'.
        model_description = self._context.get('model_description')
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                new_attachment_ids.reverse()
                wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            ActiveModel = self.env[wizard.model] if wizard.model and hasattr(self.env[wizard.model], 'message_post') else self.env['mail.thread']
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(ast.literal_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            for res_ids in sliced_res_ids:
                # mass mail mode: mail are sudo-ed, as when going through get_mail_values
                # standard access rights on related records will be checked when browsing them
                # to compute mail values. If people have access to the records they have rights
                # to create lots of emails in sudo as it is consdiered as a technical model.
                batch_mails_sudo = self.env['mail.mail'].sudo()
                all_mail_values = wizard.get_mail_values(res_ids)
                for res_id, mail_values in all_mail_values.items():
                    if wizard.composition_mode == 'mass_mail':
                        batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                    else:
                        post_params = dict(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            email_layout_xmlid=notif_layout,
                            add_sign=not bool(wizard.template_id),
                            mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else self._context.get('mail_auto_delete', True),
                            model_description=model_description)
                        post_params.update(mail_values)
                        if ActiveModel._name == 'mail.thread':
                            if wizard.model:
                                post_params['model'] = wizard.model
                                post_params['res_id'] = res_id
                            if not ActiveModel.message_notify(**post_params) and not self.emailto:
                                # if message_notify returns an empty record set, no recipients where found.
                                raise UserError(_("No recipient found."))
                        else:
                            ActiveModel.browse(res_id).message_post(**post_params)

                if wizard.composition_mode == 'mass_mail':
                    batch_mails_sudo.send(auto_commit=auto_commit)
