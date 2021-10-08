from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models,_
from datetime import datetime,timedelta

class SaleSubmission(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleSubmission, self).default_get(fields)
        # current_date_temp = datetime.strptime(str(self.date_order), "%Y-%m-%d %H:%M:%S")
        newdate = datetime.today() + timedelta(days=5)
        res.update({
            'submission_date': newdate,
        })
        return res

    submission_date=fields.Date(string="Submission Date")
    reason_id = fields.Many2one('reason.master', string='Reason')
    apply_status = fields.Selection([('yes', 'Yes'),('no', 'No')],string="Apply Status")
    responses = fields.Selection([('manual', 'Manual'),('system', 'System')],string="Response",default="system")
    version = fields.Char(String="Version",default="V1",tracking=1,readonly=1)
    check_proposal = fields.Boolean(String="Is proposal")
    count = fields.Integer(String="Count",default="1")
    priority = fields.Integer(String="Priority")
    priority_select = fields.Selection(
        [('one', 'One'), ('two', 'Two'), ('three', 'Three'), ('four', 'Four')], string="Priority")
    application_name = fields.Char(String="Application Name")
    author = fields.Char(String="Author")
    approval_need = fields.Many2one('hr.employee', string='Approval')
    assign_many_proposal = fields.Many2many('ir.actions.report', string='Proposals',domain="[('model','=','sale.order')]")
    no_of_login = fields.Integer(String="Number of Login Modules")
    no_of_modules = fields.Integer(String="Number of Modules")
    total_no_of_pages = fields.Integer(String="Total Number of Pages")
    no_of_dynamic_pages = fields.Integer(String="Number of Dynamic pages")
    no_of_application_role = fields.Integer(String="Number of Application Roles")
    cms_present = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Is CMS present")
    payment_present = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Is payment gateway present")
    shores = fields.Selection([('offshores', 'OffShore'), ('onshore', 'OnSite')], string="Location of Audit")
    no_audits = fields.Selection(
        [('one', 'One'), ('two', 'Two'), ('three', 'Three'), ('four', 'Four'), ('five', 'Five'), ('six', 'Six'),
         ('seven', 'Seven'), ('eight', 'Eight'), ('nine', 'Nine'), ('ten', 'Ten')], string="Re-Audits")



    def action_quotation_send(self):
        res =super(SaleSubmission, self).action_quotation_send()
        self.check_proposal = False
        return res

    def action_smart_leave_views(self):
        if self.user_id:
            action = {
                'res_model': 'hr.leave',
                'type': 'ir.actions.act_window',
            }
            action.update({
                'name': 'Leave',
                'domain': [('employee_id.user_id', '=', self.user_id.id),],
                'view_mode': 'tree',
            })
            return action

    def action_smart_salesperson_utilise_views(self):
        if self.user_id:
            action = {
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
            }
            action.update({
                'name': 'Salesperson Utilisation',
                'domain': [('user_id', '=', self.user_id.id),],
                'view_mode': 'tree',
            })
            return action


# class SalesMail(models.TransientModel):
#     _inherit = 'mail.compose.message'
#
#     def action_send_mail(self):
#         res = super(SalesMail, self).action_send_mail()
#         active_model = self.env.context.get('active_model')
#         if active_model =='sale.order':
#             active_id = self.env.context.get('active_id')
#             sales_id = self.env['sale.order'].search([('id', '=', active_id)])
#             collect = sales_id.version
#             if sales_id.count == 1:
#                 sales_id.count+= 1
#             else:
#                 convert = 'V' + str(int(collect.replace('V', '')) + 1)
#                 sales_id.version = convert
#         return res
#
