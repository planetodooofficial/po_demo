from odoo import api, fields, models, _,tools
from datetime import datetime,date,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import xlrd

class Employee(models.Model):
    _inherit = 'hr.employee'

    probation_ending_date = fields.Date("Probation Ended on",compute='compute_probation_end')

    @api.depends('join_date')
    def compute_probation_end(self):
        for rec in self:
            if rec.join_date:
                rec.probation_ending_date = rec.join_date + timedelta(days=30*6)
            else:
                rec.probation_ending_date = False


    def default_leave_type(self):
        leave_types = self.env['hr.leave.type'].search([])
        type_ids =[]
        for leave_type in leave_types:
            type_ids.append(self.env['employee.leave.policy'].create({
                'leave_type':leave_type.id
            }).id)
        return [(6, 0, type_ids)]

    leaves = fields.One2many('employee.leave.policy','employee',"Leave Info",default=default_leave_type)

class EmpLeavePolicy(models.Model):
    _name = 'employee.leave.policy'

    employee = fields.Many2one('hr.employee')
    leave_type = fields.Many2one('hr.leave.type',"Leave Type")
    leaves_credited = fields.Float("Credited Leaves",compute='compute_leaves_credited')
    leaves_balance = fields.Float("Leaves allowed")
    prev_year_with_leave =  fields.Char()
    carry_forwarded_leaves = fields.Float("Carry Forwarded Leaves")
    excess_leaves = fields.Float("Excess Leaves")
    restrict_excess_leave = fields.Boolean(compute='restrict_excess_leaves')
    previous_month = fields.Char()

    @api.depends('employee.parent_id')
    def restrict_excess_leaves(self):
        if self.employee.parent_id.user_id.id == self.env.user.id:
            self.restrict_excess_leave = False
        else:
            self.restrict_excess_leave = True

    @api.depends('leave_type')
    def compute_leaves_credited(self):
        for rec in self:
            today = date.today()

            ####################Leaves will be considered only after probation######################
            date_start = False
            if rec.employee.probation_ending_date:
                if rec.employee.probation_ending_date < rec.leave_type.validity_start:
                    date_start = rec.leave_type.validity_start
                if rec.employee.probation_ending_date > rec.leave_type.validity_start:
                    date_start = rec.employee.probation_ending_date

            ###########Leave Credited############################

                if date_start and rec.leave_type.validity_stop:
                    if today >= date_start and today <= rec.leave_type.validity_stop:
                        days = (today - date_start).days
                        if days < 30:
                            diff = 1
                        else:
                            diff = round(days/30)
                        leaves_credited = rec.leave_type.monthly_leaves * diff if rec.leave_type.pro_rata else rec.leave_type.no_of_leaves_allowed
                        if not rec.prev_year_with_leave:
                            rec.prev_year_with_leave = (date.strftime(rec.leave_type.validity_start,"%Y"))+ ":" +(date.strftime(rec.leave_type.validity_start,"%Y")) + ":" + str(rec.leaves_balance)
                        prev_year_start = rec.prev_year_with_leave.split(':')[0]
                        prev_year_stop = rec.prev_year_with_leave.split(':')[1]
                        prev_year_leaves = rec.prev_year_with_leave.split(':')[2]
                        if ((date.strftime(rec.leave_type.validity_start,"%Y"))+ ":" +(date.strftime(rec.leave_type.validity_start,"%Y"))) != (prev_year_start+":"+prev_year_stop):
                            if rec.leave_type.carry_forward < int(prev_year_leaves):
                                rec.carry_forwarded_leaves = rec.leave_type.carry_forward
                            else:
                                rec.carry_forwarded_leaves = int(prev_year_leaves)


                        leaves_credited += rec.carry_forwarded_leaves
                        rec.leaves_credited = leaves_credited

            if not rec.previous_month:
                rec.previous_month = str(today.month)
            if rec.previous_month != str(today.month):
                if rec.leave_type.pro_rata:
                    if rec.excess_leaves > rec.leave_type.monthly_leaves:
                        rec.excess_leaves -= rec.leave_type.monthly_leaves
                    elif rec.excess_leaves > 0 and rec.excess_leaves < rec.leave_type.monthly_leaves:
                        rec.excess_leaves -= rec.excess_leaves



            #################Leave Balance##########################

            domain = [('employee_id','=',rec.employee.id),('holiday_status_id','=',rec.leave_type.id),('state','=','validate'),
                      ('request_date_from','>=',rec.leave_type.validity_start),('request_date_from','<=',rec.leave_type.validity_stop),
                      ('request_date_to','>=',rec.leave_type.validity_start),('request_date_to','<=',rec.leave_type.validity_stop)]

            leaves = self.env['hr.leave'].search(domain)
            leaves_taken = 0.0
            for leave in leaves:
                leaves_taken += leave.number_of_days
                no_of_days = 0
                for holiday in leave.employee_id.resource_calendar_id.global_leave_ids:
                    holidays = (holiday.date_to - holiday.date_from).days
                    if holidays == 0:
                        if leave.date_from <= holiday.date_from <= leave.date_to:
                            no_of_days +=1
                leaves_taken -= no_of_days
            rec.leaves_balance = (rec.leaves_credited - leaves_taken) + (rec.excess_leaves if rec.leave_type.pro_rata else 0)
            rec.leaves_balance += rec.leave_type.leaves_in_tenure

        #########Updating Prev_Year_and_Leaves################################################################
            if rec.leave_type.validity_start:
                rec.prev_year_with_leave = (date.strftime(rec.leave_type.validity_start, "%Y")) + ":" + (
                    date.strftime(rec.leave_type.validity_start, "%Y")) + ":" + str(rec.leaves_balance)

