from odoo import api, fields, models, _,tools
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,date

class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    no_of_leaves_allowed = fields.Float("Leaves per year")
    monthly_leaves = fields.Float("Monthly Leaves",compute='cal_monthly_leave')
    carry_forward = fields.Float("Can Carry Forward")
    apply_at_a_time = fields.Float("Can Apply at a time")
    leaves_in_tenure = fields.Float("Leaves in tenure")
    pro_rata = fields.Boolean("Pro Rata ?")


    def cal_monthly_leave(self):
        for rec in self:
            if rec.leaves_in_tenure:
                rec.monthly_leaves = 0
                rec.carry_forward = 0
                rec.no_of_leaves_allowed = 0
            else:
                if rec.no_of_leaves_allowed and rec.pro_rata:
                    rec.monthly_leaves = rec.no_of_leaves_allowed /12
                else:
                    rec.monthly_leaves = 0


    @api.onchange('leaves_in_tenure')
    def unset_yearly_leaves(self):
        if self.leaves_in_tenure:
            self.monthly_leaves = 0
            self.carry_forward = 0
            self.no_of_leaves_allowed = 0

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.onchange('holiday_status_id')
    def check_mater_pater_leaves(self):
        for rec in self:
            if rec.holiday_status_id and ("Paternity Leave" in rec.holiday_status_id.name):
                paternity_leave = self.env['hr.leave.type'].search([('name','like',"Paternity Leave")],limit=1)
                paternity_leaves = self.env['hr.leave'].search([('holiday_status_id.id','=',paternity_leave.id)])
                if len(paternity_leaves) == 2:
                    raise ValidationError(_('%s\'s can be availed up to two times within the tenure in the company!!' % paternity_leave.name))

            if rec.holiday_status_id and ("Maternity Leave" in rec.holiday_status_id.name):
                maternity_leave = self.env['hr.leave.type'].search([('name', 'like', "Maternity Leave")], limit=1)
                maternity_leaves = self.env['hr.leave'].search([('holiday_status_id.id', '=', maternity_leave.id)])
                if len(maternity_leaves) == 2:
                    raise ValidationError(_('%s\'s can be availed up to two times within the tenure in the company!!' % maternity_leave.name))

    @api.onchange('number_of_days')
    def leave_at_a_time(self):
        for rec in self:
            # if "Earned Leave" in rec.holiday_status_id.name and (rec.request_unit_half or rec.request_unit_hours):
            #     raise ValidationError(_('Earned leave can be availed in multiples of one !!'))
            # if "Casual Leave" in rec.holiday_status_id.name and rec.request_unit_hours:
            #     raise ValidationError(_('Casual leave cannot be availed in custom hours !!'))
            if rec.number_of_days :
                if not rec.employee_id.probation_ending_date:
                    raise ValidationError(_('Please provide joining date for an employee !!'))

                if rec.employee_id.probation_ending_date > date.today():
                    raise ValidationError(_('You cannot apply leaves before completing probation period !!'))

                if rec.holiday_status_id.apply_at_a_time and rec.number_of_days > rec.holiday_status_id.apply_at_a_time:
                    raise ValidationError(_('Maximum of %s %s\'s can be availed at a time !!' % (rec.holiday_status_id.apply_at_a_time,rec.holiday_status_id.name)))

                for leave_data in rec.employee_id.leaves:
                    if leave_data.leave_type == rec.holiday_status_id and rec.number_of_days > leave_data.leaves_balance:
                        raise ValidationError(_('You have %s balanced leaves!!' % leave_data.leaves_balance))



