from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class HrContract(models.Model):
    _inherit = 'hr.contract'

    sent_for_approval = fields.Boolean()
    approved = fields.Boolean()
    job_id = fields.Many2one('hr.job', compute='_compute_employee_contract', store=True, readonly=False,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('state', '=', 'recruit')]",
                             string='Job Position')
    join_date = fields.Date("DOJ(ddmmyyyy)")

    def action_unarchive(self):
        res = super(HrContract, self).action_unarchive()
        if self.sent_for_approval == True:
            raise ValidationError("The contract needs to be approve first !")
        return res

    @api.model_create_multi
    def create(self, vals):
        contract = super(HrContract, self).create(vals)
        contract.sent_for_approval = True
        contract.active = False
        return contract

    def approve_contract(self):
        users_send = self.env['res.users'].search([])
        print(users_send)
        for res in users_send:
            if res.assign_role and res.login and self.employee_id.name and self.join_date and self.department_id.name and self.employee_id.work_location and self.employee_id.parent_id.name and self.employee_id.work_phone:
                for roles in res.assign_role:
                    if roles.name == 'Admin' or roles.name == 'IT' or roles.name == 'HR':
                        mail_values_admin = {}
                        mail_values_admin.update({
                            'body_html': """<head><style>table,td{
                                    border: 1px solid black;}
                                        table {
                                          border-collapse: collapse;
                                          width: 100%;
                                        }
                                                    td {
                                                      text-align: center;
                                                    }</style></head>
                                     <p>Dear All,</p>
                                    <p>Please note that """ + self.employee_id.name + """ is joining SecurEyes on """ + str(
                                self.join_date) + """. <br/>
                                                                          <br/>Below are the details:
                                                                          <table>
                                                                              <tr>
                                                                                <td><b>Employee ID</b></td>
                                                                                <td>""" + str(
                                self.employee_id.employee_no) + """</td>
                                                                              </tr>
                                                                              <tr>
                                                                                <td><b>Department</b></td>
                                                                                <td>""" + self.department_id.name + """</td>
                                                                              </tr>
                                                                              <tr>
                                                                                <td><b>Location</b></td>
                                                                                <td>""" + self.employee_id.work_location + """</td>
                                                                              </tr>
                                                                              <tr>
                                                                                <td><b>Reporting Manager</b></td>
                                                                                <td>""" + self.employee_id.parent_id.name + """</td>
                                                                              </tr>
                                                                              <tr>
                                                                                <td><b>Contact Number</b></td>
                                                                                <td>""" + str(
                                self.employee_id.work_phone) + """</td>
                                                                              </tr>
                                                                            </table>
                                                                             <p><b>Please initiate the onboarding process for your respective department.</b></p>

                                                                                                          """
                        })
                        mail_values_admin.update({
                            'subject': 'New employee joinee ',
                            'email_to': res.login,

                        })
                        msg_id_managaer = self.env['mail.mail'].create(mail_values_admin)
                        msg_id_managaer.sudo().send()
                    else:
                        print(res)
        if self.employee_id:
            if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
                if self.employee_id.parent_id.parent_id and self.employee_id.parent_id.parent_id.work_email:
                    if self.employee_id.name and self.join_date and self.department_id.name and self.employee_id.work_location and self.employee_id.parent_id.name and self.employee_id.work_phone:
                        mails =[]
                        mail_values_l2 = {}
                        mail_values_l1 = {}
                        message = """<head><style>table,td{
                                        border: 1px solid black;}
                                            table {
                                              border-collapse: collapse;
                                              width: 100%;
                                            }
                                                        td {
                                                          text-align: center;
                                                        }</style></head>
                                         <p>Dear All,</p>
                                        <p>Please note that """ + self.employee_id.name + """ is joining SecurEyes on """ + str(
                                self.join_date) + """. <br/>
                                                                              <br/>Below are the details:
                                                                              <table>
                                                                                  <tr>
                                                                                    <td><b>Employee ID</b></td>
                                                                                    <td>""" + str(
                                self.employee_id.employee_no) + """</td>
                                                                                  </tr>
                                                                                  <tr>
                                                                                    <td><b>Department</b></td>
                                                                                    <td>""" + self.department_id.name + """</td>
                                                                                  </tr>
                                                                                  <tr>
                                                                                    <td><b>Location</b></td>
                                                                                    <td>""" + self.employee_id.work_location + """</td>
                                                                                  </tr>
                                                                                  <tr>
                                                                                    <td><b>Reporting Manager</b></td>
                                                                                    <td>""" + self.employee_id.parent_id.name + """</td>
                                                                                  </tr>
                                                                                  <tr>
                                                                                    <td><b>Contact Number</b></td>
                                                                                    <td>""" + str(
                                self.employee_id.work_phone) + """</td>
                                                                                  </tr>
                                                                                </table>
                                                                                <p><b>Please initiate the onboarding process for your respective department.</b></p>
                                                                                                              """

                        mail_values_l2.update({
                            'body_html':message,
                            'subject': 'New joinee Details',
                            'email_to': self.employee_id.parent_id.parent_id.work_email
                        })
                        mail_values_l1.update({
                            'body_html':message,
                            'subject': 'New joinee Details',
                            'email_to': self.employee_id.parent_id.work_email
                        })
                        msg_id_managaer_l1 = self.env['mail.mail'].create(mail_values_l1)
                        msg_id_managaer_l2 = self.env['mail.mail'].create(mail_values_l2)
                        msg_id_managaer_l1.sudo().send()
                        msg_id_managaer_l2.sudo().send()
        self.active = True
        self.sent_for_approval = False
