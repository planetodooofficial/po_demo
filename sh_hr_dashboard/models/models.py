# Part of Softhealer Technologies.
from odoo import models, fields


class HR(models.Model):
    _inherit = 'hr.employee'

    date_of_joining = fields.Date("Date of Joining")


class HRPublic(models.Model):
    _inherit = 'hr.employee.public'

    date_of_joining = fields.Date("Date of Joining")


class HRDashboard(models.Model):
    _name = 'sh.hr.dashboard'
    _description = 'HR Dashboard'

    def create_expense(self):
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if employee:

            return {
                'name': "Expense",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.expense',
                'target': 'current',
                'context': {'default_employee_id': employee.id}
            }

    def create_attendance(self):
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if employee:
            attendance = self.env['hr.attendance'].sudo().search(
                [('check_out', '=', False), ('employee_id', '=', employee.id)], order='id desc', limit=1)
            if attendance:
                return {
                    'name': "Attendance",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.attendance',
                    'target': 'current',
                    'res_id': attendance.id
                }
            else:
                return {
                    'name': "Attendance",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.attendance',
                    'target': 'current',
                    'context': {'default_employee_id': employee.id}
                }

    def create_leave(self):
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if employee:

            return {
                'name': "Leave Request",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.leave',
                'target': 'current',
                'context': {'default_employee_id': employee.id}
            }

    def open_employee_leave(self):

        return {
            'name': "Leaves",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form,activity',
            'res_model': 'hr.leave',
            'domain': [('employee_id.user_id', '=', self.env.user.id)],
            'target': 'current',
        }

    def get_leave_count(self):
        for rec in self:
            rec.leave_count = 0
            rec.allocated_leave_count = 0
            allocated_leaves = self.env['hr.leave.allocation'].sudo().search(
                [('employee_id.user_id', '=', self.env.user.id), ('state', '=', 'validate')])
            for allocated_leave in allocated_leaves:
                rec.allocated_leave_count += allocated_leave.number_of_days

            requested_leaves = self.env['hr.leave'].sudo().search(
                [('employee_id.user_id', '=', self.env.user.id), ('state', '=', 'validate')])
            for requested_leave in requested_leaves:
                rec.leave_count += requested_leave.number_of_days

    def open_employee_attendnace(self):

        return {
            'name': "Attendance",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'res_model': 'hr.attendance',
            'domain': [('employee_id.user_id', '=', self.env.user.id)],
            'target': 'current',
        }

    def get_attendance_count(self):
        for rec in self:
            rec.attendance_count = self.env['hr.attendance'].sudo().search_count(
                [('employee_id.user_id', '=', self.env.user.id)])

    def open_employee_expense(self):

        return {
            'name': "Expense",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,graph,pivot,activity',
            'res_model': 'hr.expense',
            'domain': [('employee_id.user_id', '=', self.env.user.id)],
            'target': 'current',
        }

    def get_expense_count(self):
        for rec in self:
            rec.expense_count = 0
            expenses = self.env['hr.expense'].sudo().search(
                [('employee_id.user_id', '=', self.env.user.id)])
            if expenses:
                for expense in expenses:
                    rec.expense_count += expense.total_amount

    def open_employee_contract(self):

        return {
            'name': "Contract",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form,activity',
            'res_model': 'hr.contract',
            'domain': [('employee_id.user_id', '=', self.env.user.id)],
            'target': 'current',
        }

    def get_contract_count(self):
        for rec in self:
            rec.contract_count = self.env['hr.contract'].sudo().search_count(
                [('employee_id.user_id', '=', self.env.user.id)])

    def get_login_user(self):
        for rec in self:
            rec.user_id = self.env.uid

    name = fields.Char("Name")
    user_id = fields.Many2one(
        'res.users', string="User", compute='get_login_user')
    leave_count = fields.Integer("Leave Count", compute='get_leave_count')
    allocated_leave_count = fields.Integer(
        "Allocated Leave Count", compute='get_leave_count')
    attendance_count = fields.Integer(
        "Attendance Count", compute='get_attendance_count')
    expense_count = fields.Integer(
        "Expense Count", compute='get_expense_count')
    contract_count = fields.Integer(
        "Contract Count", compute='get_contract_count')
