from odoo import api, fields, models, _,tools
from datetime import datetime, date
from odoo.exceptions import UserError

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    show_approve = fields.Boolean(help="Used to hide show an Approve button")
    project = fields.Many2one('project.project',"For Project")

    def approve_entry(self):
        self.write({'state':'reported'})

    @api.onchange('date')
    def check_pre_post_entries(self):
        if self.date:
            date_today = datetime.strftime(datetime.today(), "%d")
            month_today = datetime.strftime(datetime.today(), "%m")
            year_today = datetime.strftime(datetime.today(), "%y")
            date_entry = datetime.strftime(self.date, "%d")
            month_entry = datetime.strftime(self.date, "%m")
            year_entry = datetime.strftime(self.date, "%y")
            if month_entry == month_today and year_entry == year_today:
                if int(date_today) > 15 and int(date_entry) < 15:
                    self.show_approve = True
                    self.state = 'draft'
                elif int(date_today) < 16 and int(date_entry) >= 16:
                    self.show_approve = True
                    self.state = 'draft'

            elif year_entry != year_today or month_entry != month_today:
                self.show_approve = True
                self.state = 'draft'