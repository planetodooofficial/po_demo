from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _
import re
import pdb

class RoleMapping(models.Model):
    _name = 'role.mapping'
    _rec_name = 'roles_assign'

    roles_assign = fields.Many2one('access.rights.master',string="Roles Name")
    objectives_assign = fields.One2many('role.mapping.line', inverse_name='role_assign_map',required=True)
    select_admin = fields.Selection([('admin', 'Admin'),('manager', 'Manager')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status', default="draft", readonly=True, tracking=True)



class RoleMappingLine(models.Model):
    _name = 'role.mapping.line'

    role_assign_line = fields.Many2one('objective.master',string="role assign")
    role_okr_line = fields.Many2one('okr.master',string="role okr")
    role_assign_map = fields.Many2one('role.mapping',string="Role assign map")
    key_skill_many_role = fields.Many2many('key.results',string="Key Results")
    # employee_rating = fields.Selection([('one', '1'), ('two', '2'),('three', '3'), ('four', '4'),('five', '5')],string="Employee Rating")
    # manager_rating = fields.Selection([('one', '1'), ('two', '2'),('three', '3'), ('four', '4'),('five', '5')],string="Manager Rating")
    employe_comments = fields.Text(string="Employee comments")
    manager_comments = fields.Text(string="Manager's comments")
    objective_weight= fields.Float(string="Objective Weightage")
    employee_ratings = fields.Integer(string="Employee Rating")
    manager_ratings = fields.Integer(string="Managers Rating")

    @api.model_create_multi
    def create(self,vals):
        res = super(RoleMappingLine, self).create(vals)
        parent = res['role_okr_line'] if 'role_okr_line' in res else False
        if parent:
            if parent.states != 'okr_settings':
                raise ValidationError(_('Cannot add line now !!'))
        return res

    @api.onchange('role_assign_line')
    def _onchange_roles_keys(self):
        if self.role_assign_line:
            self.key_skill_many_role = [(6, 0,self.role_assign_line.key_skill_many.ids)]
            self.objective_weight = self.role_assign_line.objective_weight
            pass


    def unlink(self):
        if self.role_okr_line.states != 'okr_settings':
            raise ValidationError(_('Cannot delete line now !!'))
        return super(RoleMappingLine, self).unlink()

    @api.constrains('employee_ratings','manager_ratings')
    def _check_number(self):
        for rec in self:
            if rec.employee_ratings:
                is_digits_only = re.match(r'^[1-5]+$', str(rec.employee_ratings))
                if not is_digits_only:
                    raise ValidationError(_('Objective Rating should be between 1 to 5'))
            if rec.manager_ratings:
                is_digits_only = re.match(r'^[1-5]+$', str(rec.manager_ratings))
                if not is_digits_only:
                    raise ValidationError(_('Objective Rating should be between 1 to 5'))

class ValuesMappingLine(models.Model):
    _name = 'values.mapping.line'

    values_store = fields.Many2one('value.master', string="Values")
    values_store_okr = fields.Many2one('okr.master', string="Values okr")
    value_weight = fields.Float(string="Values Weightage")
    employe_comments_for_values = fields.Text(string="Employee comments")
    manager_comments_for_values = fields.Text(string="Manager's comments")
    employee_values_ratings = fields.Integer(string="Employee Rating")
    manager_values_ratings = fields.Integer(string="Managers Rating")

    @api.model_create_multi
    def create(self,vals):
        res = super(ValuesMappingLine, self).create(vals)
        parent = res['values_store_okr'] if 'values_store_okr' in res else False
        if parent:
            if parent.states != 'okr_settings':
                raise ValidationError(_('Cannot add line now !!'))
        return res

    def unlink(self):
        if self.values_store_okr.states != 'okr_settings':
            raise ValidationError(_('Cannot delete line now !!'))
        return super(ValuesMappingLine, self).unlink()

    @api.onchange('values_store')
    def _onchange_values_keys(self):
        if self.values_store:
            self.value_weight = self.values_store.value_weight
            pass

    @api.constrains('employee_values_ratings', 'manager_values_ratings')
    def _check_number(self):
        for rec in self:
            if rec.employee_values_ratings:
                is_digits_only = re.match(r'^[1-5]+$', str(rec.employee_values_ratings))
                if not is_digits_only:
                    raise ValidationError(_('Values Rating should be between 1 to 5'))
            if rec.manager_values_ratings:
                is_digits_only = re.match(r'^[1-5]+$', str(rec.manager_values_ratings))
                if not is_digits_only:
                    raise ValidationError(_('Values Rating should be between 1 to 5'))