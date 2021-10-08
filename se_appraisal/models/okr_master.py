from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import re
from odoo.modules.module import get_module_resource
import base64


class OkrMaster(models.Model):
    _name = 'okr.master'
    _rec_name = 'roles_assign_mapp'

    @api.model
    def default_get(self, fields):
        vals = super(OkrMaster, self).default_get(fields)
        doc_path_value = get_module_resource('se_appraisal', 'static/pdf', 'Value_framework.docx')
        doc_path_ratings = get_module_resource('se_appraisal', 'static/pdf', 'Definition_of_ratings.docx')
        doc_path_Performance = get_module_resource('se_appraisal', 'static/pdf', 'Performance_Management_framework.docx')
        vals['value_framework'] = base64.b64encode(open(doc_path_value, 'rb').read())
        vals['defin_rating'] = base64.b64encode(open(doc_path_ratings, 'rb').read())
        vals['perform_policy'] = base64.b64encode(open(doc_path_Performance, 'rb').read())

        return vals

    @api.model
    def _default_documents_values(self):
        doc_path = get_module_resource('se_appraisal', 'static/pdf', 'Value_framework.docx')
        return base64.b64encode(open(doc_path, 'rb').read())

    @api.model
    def _default_documents_rating(self):
        doc_path = get_module_resource('se_appraisal', 'static/pdf', 'Definition_of_ratings.docx')
        return base64.b64encode(open(doc_path, 'rb').read())

    @api.model
    def _default_documents_policy(self):
        doc_path = get_module_resource('se_appraisal', 'static/pdf', 'Performance_Management_framework.docx')
        return base64.b64encode(open(doc_path, 'rb').read())

    annual_rating = fields.Selection([('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'),('five', '5')],string="Annual Rating")
    overall_anual_rating = fields.Float("Overall OKR Rating")
    overall_value_rating = fields.Float("Overall OKR Rating")
    overall_anual_comment = fields.Text("Overall OKR Rating")
    employee_master = fields.Many2one('hr.employee', string="Employee")
    quarters = fields.Many2one('quarter.master', string="Quarter")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date to")
    year = fields.Char(string="Year")
    roles_assign_mapp = fields.Many2one('role.mapping', string="Role")
    okr_mapp_role = fields.One2many('role.mapping.line', inverse_name='role_okr_line')
    values_mapp_role = fields.One2many('values.mapping.line', inverse_name='values_store_okr')
    states = fields.Selection([('okr_settings',"OKR Settings"),('manager_approval','Manager Approval'),('self_appraisal', 'Self Appraisal'),('manager_apraisal', 'Manager Appraisal'),('hr_appraisal', 'HR Approval'), ('done', 'Done')],
        string='Status', default="okr_settings", readonly=True, tracking=True)
    manager_overall_comments = fields.Text(string="Manager Overall Comments")
    employee_overall_ratings = fields.Float(string="Employee Overall Rating",compute='_onchange_roles_okr_assign')
    manager_overall_ratings = fields.Float(string="Manager Overall Rating",compute='_onchange_roles_okr_assign')
    employee_overall_comments = fields.Text(string="Employee Overall Comments")
    hr_overall_comments = fields.Text(string="HR Overall Comments")
    self_appraisal = fields.Boolean(compute='compute_self_appraisal')
    manager_appraisal = fields.Boolean(compute='compute_manager_appraisal')
    manager_approve = fields.Boolean(compute='compute_manager_approve')
    hr_appraisal = fields.Boolean(compute='compute_hr_appraisal')
    is_quarter = fields.Boolean(string="Is quarter",compute='annual_rating_visibility')
    note = fields.Text("Note",default="Note: All rating should be given in range of 1 to 5, where 1 is the lowest and 5 is the highest",readonly=1)

    int_rating = fields.Boolean(compute='compute_int_rating')
    manager_int_rating = fields.Integer()
    emp_int_rating = fields.Integer()
    percentages = fields.Float("Percentages")

    manager = fields.Many2one('hr.employee')
    department = fields.Many2one('hr.department')
    file_name = fields.Char("File Name")
    defin_rating = fields.Binary(string='Definition of rating',default=_default_documents_rating)
    value_framework = fields.Binary(string='Meaning of the values')
    perform_policy = fields.Binary(string='Performance management policy upload',default=_default_documents_policy)

    def compute_int_rating(self):
        for rec in self:
            rec.manager_int_rating = int(rec.manager_overall_ratings)
            rec.emp_int_rating = int(rec.employee_overall_ratings)
            rec.int_rating = True
            emp_count = self.env['hr.employee'].search_count([])
            rec.percentages = (1 / emp_count)


    def manager_approval(self):
        if self.states =='manager_approval':
            self.write({'states':'self_appraisal'})

    @api.depends('states')
    def compute_manager_approve(self):
        user = self.env.user
        for rec in self:
            if rec.states == 'manager_approval' and rec.employee_master.parent_id.user_id == user:
                rec.manager_approve = True
            else:
                rec.manager_approve = False

    @api.depends('states')
    def compute_hr_appraisal(self):
        user = self.env.user
        for rec in self:
            if rec.states == 'done':
                rec.hr_appraisal = True
            else:
                if rec.states == 'hr_appraisal' and user.has_group('hr.group_hr_user'):
                   rec.hr_appraisal = True
                else:
                    rec.hr_appraisal = False

    @api.depends('states')
    def compute_self_appraisal(self):
        user = self.env.user
        for rec in self:
            if rec.states == 'done':
                rec.self_appraisal = True
            else:
                if (rec.states == 'self_appraisal' and rec.employee_master.user_id == user) or (rec.states == 'manager_apraisal' and rec.employee_master.parent_id.user_id == user)\
                        or (rec.states == 'hr_appraisal' and user.has_group('hr.group_hr_user')):
                   rec.self_appraisal = True
                else:
                    rec.self_appraisal = False

    @api.depends('states')
    def compute_manager_appraisal(self):
        user = self.env.user
        for rec in self:
            if rec.states == 'done':
                rec.manager_appraisal = True
            else:
                if (rec.states == 'manager_apraisal' and rec.employee_master.parent_id.user_id == user) or (rec.states == 'hr_appraisal' and user.has_group('hr.group_hr_user')):
                    rec.manager_appraisal = True
                else:
                    rec.manager_appraisal = False

    @api.onchange('roles_assign_mapp')
    def _onchange_role_objective(self):
        if self.roles_assign_mapp:
            lines = []
            for rec in self.roles_assign_mapp.objectives_assign:
                val = {
                    'role_assign_line': rec.role_assign_line.id,
                    'key_skill_many_role': rec.key_skill_many_role.ids,
                    'objective_weight': rec.objective_weight
                }
                lines.append([0, 0, val])
            self.okr_mapp_role = lines

    @api.onchange('employee_master')
    def populate_okr_from_employee(self):
       if self.employee_master :
            lines = []
            self.roles_assign_mapp = self.employee_master.role.id
            for rec in self.roles_assign_mapp.objectives_assign:
                val = {
                    'role_assign_line': rec.role_assign_line.id,
                    'key_skill_many_role': rec.key_skill_many_role.ids,
                    'objective_weight': rec.objective_weight

                }
                lines.append([0, 0, val])
            self.okr_mapp_role = lines

    @api.onchange('quarters')
    def _onchange_quarters_assign(self):
        if self.quarters:
           self.date_from = self.quarters.date_from
           self.date_to = self.quarters.date_to
           self.year = self.quarters.years


    def annual_rating_visibility(self):
        user = self.env.user
        for rec in self:
            if (rec.quarters.name == 4 and rec.states == 'manager_apraisal' and rec.employee_master.parent_id.user_id == user) or (rec.states == 'done' and rec.quarters.name == 4):
                rec.is_quarter = True
            else:
                rec.is_quarter = False

    # @api.onchange('okr_mapp_role','values_mapp_role')
    def _onchange_roles_okr_assign(self):
        for rec in self:
            ##########Check for the percentages################
            total_cal_weight_rating = 0
            total_cal_weight_mag_rating = 0
            total_val_weight_rating = 0
            total_val_weight_mang_rating = 0
            # if self.okr_mapp_role:
            for okr in rec.okr_mapp_role:
                product_weight_ratings = okr.objective_weight * okr.employee_ratings
                total_cal_weight_rating += product_weight_ratings

                multiple_mang_weight = okr.objective_weight * okr.manager_ratings
                total_cal_weight_mag_rating += multiple_mang_weight
            # if self.values_mapp_role:
            for value in rec.values_mapp_role:
                multiple_val_weight = value.value_weight * value.employee_values_ratings
                total_val_weight_rating += multiple_val_weight

                multiple_val_mang_weight = value.value_weight * value.manager_values_ratings
                total_val_weight_mang_rating += multiple_val_mang_weight

            rec.employee_overall_ratings = (total_cal_weight_rating * 0.8) + (total_val_weight_rating * 0.2)
            rec.manager_overall_ratings = (total_cal_weight_mag_rating * 0.8) + (total_val_weight_mang_rating * 0.2)


    def submit_role(self):
        user = self.env.user
        if self.states == 'self_appraisal' and self.employee_master.user_id == user:
            tot_obj_weightage = 0
            tot_value_weightage = 0
            for objective in self.okr_mapp_role:
                tot_obj_weightage += objective.objective_weight * 100
            for value in self.values_mapp_role:
                tot_value_weightage += value.value_weight * 100

            if tot_obj_weightage > 100 or tot_obj_weightage < 100:
                raise ValidationError("The total objective weightage should be 100 !!")

            elif tot_value_weightage > 100 or tot_value_weightage < 100:
                raise ValidationError("The total value weightage should be 100 !!")

            if not self.employee_overall_comments:
                raise ValidationError("Please provide employee overall comments")

            for rec in self.okr_mapp_role:
                if not rec.employee_ratings:
                    raise ValidationError("Please provide employee ratings for objectives")
                if not rec.employe_comments:
                    raise ValidationError("Please provide employee comments for objectives")

            for rec in self.values_mapp_role:
                if not rec.employee_values_ratings:
                    raise ValidationError("Please provide employee ratings for values")
                if not rec.employe_comments_for_values:
                    raise ValidationError("Please provide employee comments for values")

            self.write({'states': 'manager_apraisal'})

        elif self.states == 'manager_apraisal' and self.employee_master.parent_id.user_id == user:
            tot_obj_weightage = 0
            tot_value_weightage = 0
            for objective in self.okr_mapp_role:
                tot_obj_weightage += objective.objective_weight * 100
            for value in self.values_mapp_role:
                tot_value_weightage += value.value_weight * 100

            if tot_obj_weightage > 100 or tot_obj_weightage < 100:
                raise ValidationError("The total objective weightage should be 100 !!")

            elif tot_value_weightage > 100 or tot_value_weightage < 100:
                raise ValidationError("The total value weightage should be 100 !!")

            if not self.manager_overall_comments:
                raise ValidationError("Please provide manager overall comments")

            for rec in self.okr_mapp_role:
                if not rec.manager_ratings:
                    raise ValidationError("Please provide manager ratings for objectives")
                if not rec.manager_comments:
                    raise ValidationError("Please provide manager comments for objectives")

            for rec in self.values_mapp_role:
                if not rec.manager_values_ratings:
                    raise ValidationError("Please provide manager ratings for values")
                if not rec.manager_comments_for_values:
                    raise ValidationError("Please provide manager comments for values")

            self.write({'states': 'hr_appraisal'})

        elif self.states == 'hr_appraisal' and user.has_group('se_hr.group_HR_hod_user'):
            if self.hr_overall_comments:
                self.write({'states': 'done'})
            else:
                raise ValidationError("Please provide HR comments")

        elif self.states == 'okr_settings' and self.employee_master.user_id == user:
            if self.okr_mapp_role:
                self.write({'states':'manager_approval'})
            else:
                ValidationError("Please set the OKR's")

            tot_obj_weightage = 0
            tot_value_weightage = 0
            for objective in self.okr_mapp_role:
                tot_obj_weightage += objective.objective_weight * 100
            for value in self.values_mapp_role:
                tot_value_weightage += value.value_weight * 100

            if tot_obj_weightage > 100 or tot_obj_weightage < 100:
                raise ValidationError("The total objective weightage should be 100 !!")

            elif tot_value_weightage > 100 or tot_value_weightage < 100:
                raise ValidationError("The total value weightage should be 100 !!")
        else:
            raise ValidationError("You can't submit as you don't have access")
        pass


    def reject_role(self):
        user = self.env.user
        if self.states == 'manager_apraisal' and self.employee_master.user_id == user:
            self.write({'states': 'self_appraisal'})
        elif self.states == 'hr_appraisal' and self.employee_master.parent_id.user_id == user:
            self.write({'states': 'manager_apraisal'})
        elif self.states == 'done' and user.has_group('se_hr.group_HR_hod_user'):
            self.write({'states': 'hr_appraisal'})
        elif self.states == 'manager_approval' and self.employee_master.user_id == user:
            self.write({'states': 'okr_settings'})
        else:
            raise ValidationError("You can't reject as you don't have access")
        pass

    def show_prev_okrs(self):
        domain=[('quarters.name','<',self.quarters.name),('employee_master.id','=',self.employee_master.id),('states','=','done')]

        return {
            'name':'Preious OKR',
            'type': 'ir.actions.act_window',
            'res_model': 'okr.master',
            'view_mode': 'form,tree',
            'views': [(False, 'list'),(False, 'form')],
            'domain':domain
        }


    @api.model_create_multi
    def create(self,vals):
        res =super(OkrMaster, self).create(vals)
        user = self.env.user
        employee = user.employee_id
        lines = []
        if employee:
            for rec in employee.role.objectives_assign:
                val = {
                    'role_assign_line': rec.role_assign_line.id,
                    'key_skill_many_role': rec.key_skill_many_role.ids,
                    'objective_weight': rec.objective_weight
                }
                lines.append([0, 0, val])
            res.okr_mapp_role = lines
            res.employee_master = employee.id
            res.roles_assign_mapp = employee.role.id
            res.manager = employee.parent_id.id
            res.department = employee.department_id.id

        same_quarter_okr = self.env['okr.master'].search(
            [('quarters', '=', res.quarters.id), ('employee_master', '=', employee.id),('id','!=',res.id)])
        if same_quarter_okr:
            raise ValidationError(_('You cannot create OKR\'s of employee for the same quarter !!!'))
        return res

    def write(self,vals):
        res = super(OkrMaster, self).write(vals)
        same_quarter_okr = self.env['okr.master'].search([('quarters','=',self.quarters.id),('employee_master','=',self.employee_master.id),('id','!=',self.ids[0])])
        if same_quarter_okr:
            raise ValidationError(_('You cannot create OKR\'s of the employee for same quarter !!!'))
        return res

    def unlink(self):
        user = self.env.user
        for rec in self:
            if rec.states != 'okr_settings' and not user.has_group('base.group_system'):
                raise ValidationError(_('OKR\'s cannot be deleted !!!'))
        super(OkrMaster, self).unlink()




    ##################### PMS alaytics #########################
    ratings = fields.Boolean(compute='compute_emp_rating_count')
    emp_rating_count = fields.Integer()
    employee_percentages = fields.Float()

    def compute_emp_rating_count(self):
        for rec in self:
            rec.ratings = True
            rec.emp_rating_count = round(rec.employee_overall_ratings)