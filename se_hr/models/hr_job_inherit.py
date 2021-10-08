from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time


class HrJobs(models.Model):
    _inherit = "hr.job"

    hiring_mangs = fields.Many2one('res.users', string="Hiring Manager",required=True)
    state = fields.Selection([
        ('new', 'Recruitment in draft'), ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='new',
        help="Set whether the recruitment process is open or closed for this job position.")

    def state_change(self):
        user = self.env.user
        if user.has_group('se_hr.group_HR_hod_user'):
            self.write({'state': 'recruit'})
            return {
                'name': 'Approve Message',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'approve.message.wizard',
                'target': 'new'
            }
        else:
            raise ValidationError(_("You do not have approval access!!"))

    opening_date = fields.Datetime("Opening Date")
    closing_date = fields.Datetime("Closing Date")

    def set_recruit(self):
        today = datetime.today()
        self.opening_date = today
        return super(HrJobs, self).set_recruit()

    def set_open(self):
        today = datetime.today()
        self.closing_date = today
        return super(HrJobs, self).set_open()

class HrJobsBase(models.AbstractModel):
    _inherit ="hr.employee.base"
#
    job_id = fields.Many2one('hr.job', 'Job Position', domain="['|',('company_id', '=', False), ('company_id', '=', company_id),('state', '=', 'recruit')]")
