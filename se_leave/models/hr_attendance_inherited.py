from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def check_out_assign(self):
        checkouts = self.env['hr.attendance'].search([])
        assign_date = datetime.now()
        for res in checkouts:
            if not res.check_out:
                if res.employee_id and res.employee_id.name and res.employee_id.work_email and res.check_in:
                    mail_values = {}
                    mail_values.update({
                        'body_html': """<p>Dear """ + res.employee_id.name + """,</p>
               <p>       You have been auto clocked out for the date:<b> """ + str(res.check_in) + """</b>, Please regularize your attendance accordingly.</p>"""
                    })
                    mail_values.update({
                        'subject': 'Attendance Update for ' + res.employee_id.name,
                        'email_to': res.employee_id.work_email,

                    })
                    msg_id_managaer = self.env['mail.mail'].create(mail_values)
                    msg_id_managaer.send()
                res.check_out = assign_date
            else:
                print(checkouts)


class HrResignationInherit(models.Model):
    _inherit = "hr.resignation"

    @api.model
    def create(self, vals):
        rec = super(HrResignationInherit, self).create(vals)
        if rec.employee_id.join_date and rec.employee_id:
            rec['joined_date']=rec.employee_id.join_date

        return rec


