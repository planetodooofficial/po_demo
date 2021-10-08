from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.modules.module import get_module_resource
import base64



class InterviewSheet(models.Model):
    _name = 'interview.sheet'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('se_hr', 'static/img', 'smiles.png')
        return base64.b64encode(open(image_path, 'rb').read())

    candidate = fields.Many2one('hr.applicant',"Candidate")
    job_position = fields.Many2one('hr.job',"Position")
    name = fields.Char(readonly=True)
    level = fields.Char(string='LEVEL')
    # clients = fields.Many2one('res.users')
    clients_name = fields.Many2one('res.partner')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)

    # Comments

    communication = fields.Char("Communication Skill (1 Low-5 High)")
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
    offer_inhand = fields.Char("Offer in hand ?")
    qualification = fields.Char("Qualification")
    certi = fields.Char("Certifications")

    #Final/Feedback Comments

    date = fields.Date("Date")
    feed_comments = fields.Text("Final & Feedback Comments")
    appl_status = fields.Selection([('reject',"Reject"),('hold',"Hold"),('select',"Select")])

    #Assesment

    claims_for_work = fields.Selection([('null',"Null"),('try_again',"Try Again"),('closer',"Getting Closer"),('ok',"OK"),
                                        ('almost_there',"Almost There"),('perfect',"Perfect")],"Candidate Claims for work")
    honesty = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Honesty")
    presentability = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Presentability")
    comm_skills = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Communication Skills")
    attitude = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Attitude/Positive Approach")
    confidence = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Confidence")
    thoughts_clarity = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Clarity of thought")
    struct_approach = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Structured Approach")
    tech_strength = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Technical Strength")
    prim_focus = fields.Selection([('job',"Job"),('money', "Money")],
                                       "Primary Focus(job/money)")
    se_fitment = fields.Selection([('null',"Null"),('try_again', "Try Again"), ('closer', "Getting Closer"), ('ok', "OK"),
                                        ('almost_there', "Almost There"), ('perfect', "Perfect")],
                                       "Fitment into SecurEyes")

    recording = fields.Binary("Audio/Video Rec.")

    allowed_users = fields.Many2many('res.users')
    owner = fields.Many2one('res.users')
    image_smiles = fields.Image(default=_default_image)



    @api.onchange('appl_status')
    def select_or_reject(self):
        if self.appl_status and self.appl_status == 'reject':
            self.candidate.is_rejected = True


    @api.model
    def default_get(self, fields_list):
        res = super(InterviewSheet, self).default_get(fields_list)
        logged_user = self.env.user
        application = self.env['hr.applicant'].search([('id','=',self.env.context['active_id'])])
        if application:
            res['candidate'] = application.id
            res['job_position'] = application.job_id.id
            res['owner'] = logged_user

            #Comments
            res['communication'] = application.communication
            res['organisation'] = application.organisation
            res['tot_exp'] = application.tot_exp
            res['rel_exp'] = application.rel_exp
            res['curr_location'] = application.curr_location
            res['pref_location'] = application.pref_location
            res['job_change_reason'] = application.job_change_reason
            res['relocation'] = application.relocation
            res['open_to_travel'] = application.open_to_travel
            res['curr_ctc'] = application.curr_ctc
            res['month_salary'] = application.month_salary
            res['expd_ctc'] = application.expd_ctc
            res['notice_period'] = application.notice_period
            res['offer_inhand'] = application.offer_inhand
            res['qualification'] = application.qualification
            res['certi'] = application.certi

            if logged_user == application.interviewer1:
                res['name'] ='IRS for Interviewer 1'
            elif logged_user == application.interviewer2:
                res['name'] ='IRS for Interviewer 2'
            elif logged_user == application.user_id:
                res['name'] ='IRS for HR'
            else:
                res['name'] = ''


        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(InterviewSheet, self).create(vals)
        application = self.env['hr.applicant'].search([('id','=',self.env.context['active_id'])])
        user = self.env.user
        if application:
            if user == application.interviewer1:
                res['allowed_users'] = [(6, 0, [application.interviewer2.id,application.user_id.id])]
            if user == application.interviewer2:
                res['allowed_users'] = [(6, 0, [application.user_id.id])]

        return res

    def write(self,vals):
        logged_user = self.env.user
        if self.owner != logged_user:
            raise ValidationError('You cannot edit the sheet !')

        return super(InterviewSheet, self).write(vals)



