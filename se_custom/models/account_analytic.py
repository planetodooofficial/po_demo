from odoo import api, fields, models, _,tools
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.line'

    # Commented as a new requirement
    initial_planned_hours = fields.Float(related='task_id.planned_hours', string="Initially Planned Hours", tracking=True)

    def _domain_employee_id(self):
        if not self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return [('user_id', '=', self.env.user.id)]
        return []

    show_approve = fields.Boolean(help="Used to hide show an Approve button")
    status = fields.Selection([('not submitted','Not Submitted'),('submitted','Submitted')],default='submitted')
    employee_id = fields.Many2one('hr.employee', "Resources", domain=_domain_employee_id)
    no_of_days = fields.Float("No. Of Days")

    # @api.onchange('no_of_days')
    # def populate_duration(self):
    #     if self.no_of_days:
    #         self.unit_amount = self.no_of_days * self.employee_id.resource_calendar_id.hours_per_day



    def approve_entry(self):
        # self.write({'status':'submitted'})
        if self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            self.write({'status':'submitted'})
        else:
            raise ValidationError("You dont have access of approval.")

    # def utilisation_record(self):
    #     domain = [('employee_id.id','=', self.employee_id.id),('project_id.id','!=', self.project_id.id)]
    #     # view_id = self.env.ref('project.open_view_project_all').id
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Resource Utilisation'),
    #         'res_model': 'account.analytic.line',
    #         'view_mode': 'tree',
    #         'views': [[False, 'list']],
    #         'domain': domain,
    #     }


    @api.model_create_multi
    def create(self, vals):
        res = super(AccountAnalytic, self).create(vals)
        for rec in res:
            if rec.date:
                date_today = datetime.strftime(datetime.today(), "%d")
                month_today = datetime.strftime(datetime.today(), "%m")
                year_today = datetime.strftime(datetime.today(), "%y")
                date_entry = datetime.strftime(rec.date, "%d")
                month_entry = datetime.strftime(rec.date, "%m")
                year_entry = datetime.strftime(rec.date, "%y")
                if month_entry == month_today and year_entry == year_today:
                    if int(date_today) > 15 and int(date_entry) < 15:
                        rec['show_approve'] = True
                        rec['status'] = 'not submitted'
                    elif int(date_today) < 16 and int(date_entry) >= 16:
                        rec['show_approve'] = True
                        rec['status'] = 'not submitted'

                elif year_entry != year_today or month_entry != month_today:
                    rec['show_approve'] = True
                    rec['status'] = 'not submitted'
                else:
                    rec['status'] = 'submitted'
        return res


    def write(self, vals):
        res = super(AccountAnalytic, self).write(vals)

        if vals.get('date'):

            date_today = datetime.strftime(datetime.today(), "%d")
            month_today = datetime.strftime(datetime.today(), "%m")
            year_today = datetime.strftime(datetime.today(), "%y")
            date_entry = datetime.strftime(self.date, "%d")
            month_entry = datetime.strftime(self.date, "%m")
            year_entry = datetime.strftime(self.date, "%y")
            if month_entry == month_today and year_entry == year_today:
                if int(date_today) > 15 and int(date_entry) < 15:
                    self.show_approve = True
                    self.status = 'not submitted'
                elif int(date_today) < 16 and int(date_entry) >= 16:
                    self.show_approve = True
                    self.status = 'not submitted'

            elif year_entry != year_today or month_entry != month_today:
                self.show_approve = True
                self.status = 'not submitted'
            else:
                self.status = 'submitted'

        return res
