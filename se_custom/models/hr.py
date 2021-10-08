from odoo import api, fields, models, tools, SUPERUSER_ID,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ActivityName(models.Model):
    _name = 'activity.name'
    _rec_name = "activity_name"

    activity_name = fields.Char(string="Activity Name")


class HrCandidateCommunication(models.Model):
    _name = 'hr.candidate.communication'

    temp_field = fields.Many2one('hr.applicant', string="temp")
    activity = fields.Many2one('activity.name', string="Activity")
    date_menu = fields.Date(string="Date")

    def action_schedule_email(self):
        mail = self.env['mail.mail']
        activity_id = self.activity.activity_name
        today = datetime.now().date()
        candidate_date = self.date_menu
        hr_date = self.date_menu - timedelta(1)
        # prev_date=datetime.strftime(hr_date,'%m/%d/%Y %H:%M:%S')
        email = self.temp_field.email_from
        user = self.temp_field.user_id.login

        if activity_id and hr_date<candidate_date:
                val = {
                    'subject': "Activity Email For Recuirter",
                    'body_html':  """ <p>Hello,<br/> Activity """ + self.activity.activity_name + """ is set
                                for candidate """ + self.temp_field.partner_name + """ on Date """ + str(candidate_date) + """ .</p> """,
                    'email_to':user,
                    'scheduled_date':hr_date,
                }
                mail.create(val)

        if activity_id and candidate_date:
                values = {
                    'subject': "Activity Email For Candidate",
                    'body_html':  """ <p>Hello """ + self.temp_field.partner_name + """,<br/></p>
                     <p><b>Your Activity """ + self.activity.activity_name + """ is set on Date """ + str(candidate_date) + """ .</b></p> """,
                    'email_to': email,
                    'custom_schedule_date': self.date_menu,
                }
                mail.create(values)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    can_comm = fields.One2many('hr.candidate.communication', 'temp_field', string="Candidate Communication")
    is_rejected = fields.Boolean("Is Rejected")
    # interviewer1 = fields.Many2many('res.users','applicant_interviewer1_rel',string="Interviewer 1")
    # interviewer2 = fields.Many2many('res.users','applicant_interviewer2_rel',string="Interviewer 2")
    interviewer1 = fields.Many2one('res.users', string="Interviewer 1")
    interviewer2 = fields.Many2one('res.users', string="Interviewer 2")

    def _find_mail_template(self):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('se_custom.email_template_refuse_candidate', raise_if_not_found=False)

        return template_id

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        emp_obj = self.env['hr.employee'].search([('job_id','=',self.job_id.id)])
        emp_count = len(emp_obj)
        if self.job_id.no_of_recruitment == 0:
            raise ValidationError('No vacancy available.')
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'default_source_id': applicant.source_id.id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.department_id and applicant.department_id.company_id
                                          and applicant.department_id.company_id.email or False,
                    'default_work_phone': applicant.department_id.company_id.phone,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        self.job_id.no_of_recruitment -= 1
        return dict_act_window

    def send_refuse_mail(self):
        template_id = self._find_mail_template()

        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
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

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    delegated_manager_id = fields.Many2one('res.users', string="Delegated Manager")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # cust_job_title = fields.Many2one('hr.job')
    emp_no = fields.Char(string="Employee No.")
    employee_no = fields.Char(string="Employee No.")
    source_id = fields.Many2one('utm.source',string="Source")
    pan = fields.Char("PAN")
    adahar = fields.Char("Adhaar NO.")
    blood_group = fields.Char("Blood Group")
    emp_type = fields.Many2one('hr.contract.type',string="Type")
    country_id = fields.Many2one('res.country', string='Country', )
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]")
    state_code = fields.Char(related='state_id.code')
    city = fields.Char('City')
    zip = fields.Char('ZIP')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    delegated_manager = fields.Many2one('res.users',string="Delegated Manager")
    delegated_expense_approver = fields.Many2one('res.users',string="Delegated Expense Approver")
    delegated_timeoff_approver = fields.Many2one('res.users',string="Delegated TimeOff Approver")

    # _sql_constraints = [
    #     ('employee_uniq', 'unique (name)',
    #      'Employee already exist with same name')
    # ]

    # @api.onchange('delegated_manager')
    # def set_delegated_accesses(self):
    #     if self.delegated_manager:
    #         self.delegated_expense_approver = self.delegated_manager.id
    #         self.delegated_timeoff_approver = self.delegated_manager.id

    @api.model_create_multi
    def create(self,vals):
        res = super(HrEmployee, self).create(vals)
        if res['emp_type']:
            emp_code = ""
            if "Employee" in res['emp_type'].name:
                emp_code = "SECON7"
            if "Admin" in res['emp_type'].name:
                emp_code = "SEADM5"
            if "Trainee" in res['emp_type'].name:
                emp_code = "SETRN1"
            seq = self.env['ir.sequence'].next_by_code('hr.employee')
            res['employee_no'] = emp_code + seq
        return res

    def write(self,vals):
        res = super(HrEmployee, self).write(vals)
        if vals.get('emp_type'):
            emp_code = ""
            if "Employee" in self.emp_type.name:
                emp_code = "SECON7"
            if "Admin" in self.emp_type.name:
                emp_code = "SEADM5"
            if "Trainee" in self.emp_type.name:
                emp_code = "SETRN1"
            seq = self.env['ir.sequence'].next_by_code('hr.employee')
            self.employee_no = emp_code + seq
        return res

    def show_alloted_projects(self):
        domain = [('user_id', '=', self.user_id.id),('is_a_template','=',False)]
        # view_id = self.env.ref('hr_timesheet.hr_timesheet_line_tree').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('My Projects'),
            'res_model': 'project.project',
            'view_mode': 'kanban,form',
            'views': [[False, 'kanban']],
            # 'view_id': view_id,
            'domain': domain,
        }

class HrRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    def action_refuse_reason_apply(self):
        if self._context.get('active_model') == 'hr.applicant':
            applicant_id = self.env['hr.applicant'].browse(self._context.get('active_id'))
            if applicant_id.is_rejected:
                if applicant_id.emp_id:
                    applicant_id.emp_id.active = False
                applicant_id.job_id.no_of_recruitment += 1
                applicant_id.job_id.no_of_employee -= 1
                # lang = self.env.context.get('lang')
                # template = self.env['mail.template'].browse(template_id)

                return self.applicant_ids.write({'refuse_reason_id': self.refuse_reason_id.id})
