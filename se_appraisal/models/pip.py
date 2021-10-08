from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class PIP(models.Model):
    _name = 'pip.bip'
    _rec_name = 'emp_id'

    active = fields.Boolean("Active",default='True')
    emp_id = fields.Many2one('hr.employee',"Employee")
    state = fields.Selection([('draft',"Draft"),('l2_approved',"L2 manager approval"),('hr_approved',"HR Approval"),('reviewed',"Review Meetings"),('closed',"Closed")],default='draft')
    designation = fields.Many2one('access.rights.master',"Designation")
    level = fields.Char("Level")
    manager = fields.Many2one('hr.employee',"Reporting Manager")
    init_meet_date = fields.Date("Initial Meeting Date")
    # prev_details = fields.One2many('previous.details','pip',string="")
    goals_outcomes = fields.One2many('goals.outcomes','pip')
    hide_approve = fields.Boolean(compute='compute_hide_approve')
    hide_submit = fields.Boolean(compute='compute_hide_submit')
    plans_steps = fields.Text("Performance improvement plans & steps:")
    ack_acceptance = fields.Text("Acknowledgement and Acceptance")
    final_status = fields.Char("Final Status")
    final_comments = fields.Text("Final Comments")
    closure = fields.Selection([('negative',"Positive"),('positive',"Negative")],"Closure")

    @api.model
    def default_get(self, fields_list):
        user = self.env.user
        res = super(PIP, self).default_get(fields_list)
        if user.employee_id:
            res['emp_id'] = user.employee_id.id
            res['manager'] = user.employee_id.parent_id.id
            res['designation'] = user.employee_id.role.id
            res['level'] = user.employee_id.level
        return res

    @api.onchange('emp_id')
    def update_emp_details(self):
        for rec in self:
            if rec.emp_id and rec.emp_id.parent_id:
                rec.manager = rec.emp_id.parent_id.id
            else:
                raise ValidationError(_('Manager is not assigned to an employee!!'))

    def close_pip(self):
        user = self.env.user
        if self.emp_id.parent_id.user_id == user or user.has_group('se_hr.group_HR_hod_user'):
            self.active = False
            self.state = 'closed'
        else:
            raise ValidationError(_('You do not have access!!'))

    def compute_hide_approve(self):
        user = self.env.user
        for rec in self:
            if rec.state == 'draft' and user == rec.emp_id.parent_id.parent_id.user_id:
                rec.hide_approve = False
            elif rec.state == 'l2_approved' and user.has_group('se_hr.group_HR_hod_user'):
                rec.hide_approve = False
            else:
                rec.hide_approve = True

    def compute_hide_submit(self):
        user = self.env.user

        for rec in self:
            if rec.state == 'hr_approved' and user == rec.emp_id.parent_id.user_id:
                rec.hide_submit = False
            else:
                rec.hide_submit = True

    def approve(self):
        if self.state == 'draft':
            self.state = 'l2_approved'
        elif self.state == 'l2_approved':
            self.state = 'hr_approved'

    def submit(self):
        if self.state == 'hr_approved':
            self.state = 'reviewed'

    @api.model_create_multi
    def create(self,vals):
        user = self.env.user
        res = super(PIP, self).create(vals)
        if res.emp_id.parent_id.user_id != user:
            raise ValidationError(_('You do not have access to initiate PIP/BIP!!'))
        return res

    def action_unarchive(self):
        res = super(PIP, self).action_unarchive()
        user = self.env.user
        if not (self.emp_id.parent_id.user_id == user or user.has_group('se_hr.group_HR_hod_user')):
            raise ValidationError(_('You do not have access to unarchive PIP/BIP!!'))
        return res

class PrevDetails(models.Model):
    _name = 'previous.details'

    name = fields.Text("Previous observations, discussions/counselling details")
    date = fields.Date("Date")
    pip = fields.Many2one('pip.bip')


class GoalsOutcomes(models.Model):
    _name = 'goals.outcomes'

    pip = fields.Many2one('pip.bip')
    meeting = fields.Many2one('pip.meeting')
    name = fields.Text("Improvement Goals/ Expected Outcomes:")
    success_criteria = fields.Text("Success Criterion")
    comments = fields.Text("Comments")
    met_notmet = fields.Boolean("Met/Not Met")
    weightage = fields.Float("Weightage")

class PipMeeting(models.Model):
    _name = 'pip.meeting'

    create_date = fields.Date("Meeting Date",default=fields.Date.today)
    pip_meeting = fields.Many2one('pip.bip')
    goals_outcomes = fields.One2many('goals.outcomes','meeting')

    @api.model
    def default_get(self, fields_list):
        res = super(PipMeeting, self).default_get(fields_list)
        pip = self.env['pip.bip'].search([('id', '=', self.env.context['active_id'])])
        res['pip_meeting'] = pip.id
        res['goals_outcomes'] = [(6, 0, pip.goals_outcomes.ids)]
        return res