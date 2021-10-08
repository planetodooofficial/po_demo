from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import datetime


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def default_stage(self):
        stages = self.env['hr.recruitment.stage'].search([])
        stage_ids = []
        for stage in stages:
            stage_ids.append(self.env['recruitment.stage.duration'].create({
                'stage_id': stage.id
            }).id)
        return [(6, 0, stage_ids)]

    refuse_hide = fields.Boolean(compute='hide_refuse')
    irs_hide = fields.Boolean(compute='hide_irs')
    stage_duration = fields.One2many('recruitment.stage.duration', 'application', default=default_stage)
    stage_duration_update = fields.Boolean(compute='set_duration')
    refer_by = fields.Many2one('hr.employee', string="Referred By")
    is_refered = fields.Boolean("Is refered")
    is_offer = fields.Boolean("Is offer", compute='set_is_offer')
    is_matching = fields.Boolean("can be hide", compute='hide_refuse')
    hide_approve = fields.Boolean("interviewer 1&2", compute='hide_inter1_2')
    current_salary = fields.Float(String='Current Salary')
    is_source = fields.Boolean("Is source", default=False)
    is_approve = fields.Boolean("Is Approve", compute='compute_is_approve')
    job_id = fields.Many2one('hr.job', "Applied Job",
                             domain="['|',('company_id', '=', False), ('company_id', '=', company_id),('state', '=', 'recruit')]",
                             tracking=True)
    offer_letter_appl = fields.Many2one('offer.letter', string="Offer letter of")

    stages = fields.Selection(
        [('sourcing', "Sourcing"), ('cv_sel', "CV Selection"), ('tech_int_1', "Technical Interview 1"),
         ('tech_int_2', "Technical Interview 2"), ('hr_int', "HR Interview"), ('cand_sel', "Candidate Selection"),
         ('offer_maker', "Offer Maker"), ('offer_checker', "Offer Checker"), ('offer_accept', "Offer Accepted"),
         ('cand_manage', "Candidate Engagement"), ('emp_create', "Employee Creation"), ('rejected', "Rejected")], string="Stages",compute='determine_stages',help="Used to determine the stages and hide the contents accordingly",store=True)
    # offer_letter_counts = fields.Integer(string="Offer letter count")

    # IRS Comments
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    communication = fields.Char("Communication Skill")
    organisation = fields.Char("Current Organisation")
    tot_exp = fields.Char("Total Experience")
    rel_exp = fields.Char("Relevant Experience")
    curr_location = fields.Char("Current Location")
    pref_location = fields.Char("Preferred Location")
    job_change_reason = fields.Char("Reason for Job Change or Not working")
    relocation = fields.Boolean("Open for Relocation")
    open_to_travel = fields.Boolean("Open to Travel as per project requirements")
    curr_ctc = fields.Monetary("Current CTC")
    month_salary = fields.Monetary("TH Salary (Monthly)")
    expd_ctc = fields.Monetary("Expected CTC & TH (nego)")
    notice_period = fields.Char("Notice Period (nego)")
    offer_inhand = fields.Boolean("Offer in hand (Yes/ No)")
    qualification = fields.Char("Qualification")
    certi = fields.Char("Certifications")


    @api.depends('stage_id')
    def determine_stages(self):
        stages = self.env['hr.recruitment.stage'].search([])
        for rec in self:
            if rec.stage_id:
                if rec.stage_id.name == "Sourcing":
                    rec.stages = 'sourcing'
                elif rec.stage_id.name == "CV Selection":
                    rec.stages = 'cv_sel'
                elif rec.stage_id.name == "Technical Interview 1":
                    rec.stages = 'tech_int_1'
                elif rec.stage_id.name == "Technical Interview 2":
                    rec.stages = 'tech_int_2'
                elif rec.stage_id.name == "HR Interview":
                    rec.stages = 'hr_int'
                elif rec.stage_id.name == "Candidate Selection":
                    rec.stages = 'cand_sel'
                elif rec.stage_id.name == "Offer Maker":
                    rec.stages = 'offer_maker'
                elif rec.stage_id.name == "Offer Checker":
                    rec.stages = 'offer_checker'
                elif rec.stage_id.name == "Offer Accepted":
                    rec.stages = 'offer_accept'
                elif rec.stage_id.name == "Candidate Engagement":
                    rec.stages = 'cand_manage'
                elif rec.stage_id.name == "Employee Creation":
                    rec.stages = 'emp_create'
                elif rec.stage_id.name == "Rejected":
                    rec.stages = 'rejected'
                else:
                    raise ValidationError("Any of the stage is not having correct name")
            else:
                rec.stages = 'sourcing'
                # raise ValidationError("Any of the stage is not having correct name")


    def approve(self):
        stages = self.env['hr.recruitment.stage'].search([])
        for i in range(len(stages)):
            stage = stages[i]
            if stage and stage == self.stage_id:
                next_page = stages[i+1]
                self.stage_id = next_page
                break

    @api.depends('offer_letter_appl')
    def compute_is_approve(self):
        for rec in self:
            if rec.offer_letter_appl and rec.offer_letter_appl.state == 'approved':
                rec.is_approve = True
            else:
                rec.is_approve = False

    @api.depends('stage_id')
    def set_duration(self):
        for rec in self:
            if rec.stage_id:
                now = datetime.today()
                # employee = self.env['hr.employee'].search([('name','=',rec.partner_name)])
                for stage in rec.stage_duration:
                    if stage.stage_id:
                        if rec.stage_id.id == stage.stage_id.id:
                            if not stage.date_start:
                                stage.write({'date_start': now})
                        elif rec.last_stage_id.id == stage.stage_id.id and not "Employee Creation" in stage.stage_id.name:
                            stage.write({'date_stop': now})
                        elif "Employee Creation" in stage.stage_id.name and stage.application.emp_id and not stage.date_stop:
                            stage.write({'date_stop': stage.application.emp_id.join_date if stage.application.emp_id.join_date else now})

                        else:
                            stage.write({'date_stop': now})

                rec.stage_duration_update = True
                rec.write({'last_stage_id': rec.stage_id.id})
            else:
                rec.stage_duration_update = False

    @api.depends('offer_letter_appl')
    def set_is_offer(self):
        for rec in self:
            if rec.offer_letter_appl:
                rec.is_offer = True
            else:
                rec.is_offer = False

    @api.depends('user_id', 'interviewer1', 'interviewer2')
    def hide_irs(self):
        user = self.env.user
        if user == self.user_id:
            irs = self.env['interview.sheet'].search([('candidate', '=', self.id), ('owner', '=', self.user_id.id)])
            if irs:
                self.irs_hide = True
            else:
                self.irs_hide = False
        elif user == self.interviewer1:
            irs = self.env['interview.sheet'].search(
                [('candidate', '=', self.id), ('owner', '=', self.interviewer1.id)])
            if irs:
                self.irs_hide = True
            else:
                self.irs_hide = False
        elif user == self.interviewer2:
            irs = self.env['interview.sheet'].search(
                [('candidate', '=', self.id), ('owner', '=', self.interviewer2.id)])
            if irs:
                self.irs_hide = True
            else:
                self.irs_hide = False
        else:
            self.irs_hide = False

    @api.depends('user_id')
    def hide_refuse(self):
        user = self.env.user
        if self.user_id == user:
            self.refuse_hide = False
            self.is_matching = True
        else:
            self.is_matching = False
            self.refuse_hide = True

    @api.depends('interviewer1','stage_id','interviewer2')
    def hide_inter1_2(self):
        user = self.env.user
        if self.interviewer1 == user and self.stages == 'tech_int_1':
            self.hide_approve = False
        elif self.interviewer2 == user and self.stages == 'tech_int_2':
            self.hide_approve = False
        elif self.user_id == user and self.stages not in ('tech_int_1','tech_int_2'):
            self.hide_approve = False
        else:
            self.hide_approve = True

    def action_show_cff(self):
        res = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_form')
        res['domain'] = [('candidate', '=', self.id)]
        return res

    def action_show_irs(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('se_hr.action_interview_rating')
        res['domain'] = [('candidate', '=', self.id)]
        return res

    @api.model
    def create(self, vals):
        res = super(HrApplicant, self).create(vals)
        if res.email_from and res.refer_by.name and res.partner_name and res.job_id.name:
            mail_values = {}
            mail_values.update({
                'body_html': """ <p>Hi """ + res.partner_name + """,</p>
                                    <p>Your name and contact information were sent to us by """ + res.refer_by.name + """, who thinks you’d be a great fit for the following open jobs at SecurEyes.</p><p>
                                    <ol style="list-style-type: inherit;">
                                      <li>""" + str(res.job_id.id) + """ – """ + res.job_id.name + """</li>
                                      </ol></p>
                                      <p>We will review your application and contact you with the next steps. We're looking to share general status of your application with """ + res.refer_by.name + """ to keep them informed.<br>
                                      You can also visit the SecurEyes careers page and find out other open positions that we currently have.
                                    </p>
                                    <p>
                                    We’re looking forward to getting to know you, and hope you’ll find the right fit at SecurEyes.
                                    </p> """
            })
            mail_values.update({
                'subject': 'Referred by ' + res.refer_by.name,
                'email_to': res.email_from,

            })
            msg_id_managaer = self.env['mail.mail'].create(mail_values)
            msg_id_managaer.sudo().send()
        else:
            print(res)
        return res

    # def _find_mail_template_offer(self):
    #     template_id = self.env['ir.model.data'].xmlid_to_res_id('se_hr.email_offer_letter_approval',
    #                                                             raise_if_not_found=False)
    #
    #     return template_id
    #
    # def send_candidate(self):
    #     template_id = self._find_mail_template_offer()
    #     ctx = {
    #         'default_model': 'hr.applicant',
    #         'default_template_id': template_id,
    #         'force_email': True,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    @api.onchange('source_id', 'refer_by')
    def on_change_source(self):
        if self.source_id:
            self.is_refered = True
        elif self.refer_by:
            self.is_source = True
            pass

    def action_create_offer_letters(self):
        self.ensure_one()
        if not self.salary_proposed:
            self.salary_proposed = 0.00
        action = {
            'res_model': 'offer.letter',
            'type': 'ir.actions.act_window',
        }
        action.update({
            'name': 'offer_letter',
            'domain': [('id', '=', self.id)],
            'view_mode': 'form',
            'context': {'default_cand_name': self.id,
                        'default_job_id': self.job_id.id,
                        'default_ctc': self.salary_proposed,
                        },
        })
        return action

    def action_smart_offer_view(self):
        self.ensure_one()
        offer_ids = self.offer_letter_appl.id
        action = {
            'res_model': 'offer.letter',
            'type': 'ir.actions.act_window',
        }
        if offer_ids:
            # if len(offer_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': offer_ids,
            })
        return action

    # def create_employee_from_applicant(self):
    #     res = super(HrApplicant, self).create_employee_from_applicant()
    #     for stage in self.stage_duration:
    #         if stage.stage_id.name == 'Employee creation':
    #             stage.date_stop = datetime.today()
    #     return res


class StageDuration(models.Model):
    _name = 'recruitment.stage.duration'

    stage_id = fields.Many2one('hr.recruitment.stage', "stage")
    application = fields.Many2one('hr.applicant')
    date_start = fields.Datetime("Start Date")
    date_stop = fields.Datetime("Stop Date")
