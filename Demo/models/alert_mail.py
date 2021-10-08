from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
from datetime import date,datetime
from datetime import timedelta


class AlertMailEmployee(models.Model):
    _inherit = 'hr.employee'

    active_flag = fields.Boolean(string='Active flag')



class JoineMailEmployee(models.Model):
    _inherit = 'employee.orientation'


    def alert_mail_doj(self):
        today = date.today()
        orient_list_seven = self.env['employee.orientation'].search([('sevenday_mail', '=', today)])

        orient_list_one = self.env['employee.orientation'].search([('oneday_mail', '=', today)])
        # employee_test = self.env['employee.orientation'].search(['id','=', self.id])
        # employe_list = self.env['hr.employee'].search([('id', '=', orient_list.employee_id.id)])
        # employe_list = self.env['hr.employee'].search([('id', '=', orient_list.employee_id.id)])
        company_list = self.env['res.partner'].search([('is_company', '=', True)])
        for emp in orient_list_seven:
            message = """<head>
                                                                    <style>
                                                        table, th, td {
                                                          border: 1px solid black;
                                                          border-collapse: collapse;
                                                        }
                                                        th, td {
                                                          padding: 5px;
                                                        }
                                                        th {
                                                          text-align: left;
                                                        }
                                                        </style>
            </head>
            <body>
            <p>Dear Mr./Ms.  """ + emp.employee_id.name + """,</p>
            <p>We are excited to welcome you on-board!!! We would like you to know more about us and for the same please refer the NEO booklet. As a part of our New Employee Onboarding process, you will soon get a Welcome call from your reporting manager,your Buddy and our Emerging Leader Club member .Looking forward to have you on-board. </p>
                                                                              <p>  <table style="width:100%">
                                            <tr>
                                            <td>DOJ</td>
                                            <td>""" + str(emp.date) + """</td>
                                            </tr>
                                            <tr>
                                            <td>Reporting Time</td>
                                            <td>""" + str(emp.delivery_time) + """</td>
                                            </tr>
                                            
                                            <tr>
                                            <td>Address</td>
                                            <td><p>""" + str(company_list.street or '-') + """</p></td>
                                            </tr>
                                            
                                            <tr>
                                            <td>Reporting Manager name and Contact Number</td>
                                            <td><p>""" + str(emp.employee_id.parent_id.name or '-') + """ </p>
                                             <p>""" + str(emp.employee_id.parent_id.work_phone or '-')+ """</p></td>
                                            </tr>
                                            
                                            <tr>
                                            <td>TEAM NEO contact number</td>
                                            <td>""" + company_list.phone + """</td>
                                            </tr>
                                            <tr>
                                            <td>Dress Code</td>
                                            <td>Formal Dress</td>
                                            </tr>
                                             </table></p>
                                             <p>We have salary account of employees in HDFC bank, incase you already have  HDFC account, request you to share HDFCSalary A/C details like- Account Number, Account Holders Name, IFSC Code, MICR Code, Address along with cancelled HDFC cheque scan copy and also share soft copy of your photograph. </p>
                                             <p>In case you do not have Account in HDFC Bank provide us your nearest HDFC Bank details in the attached format only.</p>
                                             <p>Also, provide the below details asked in the table format. These details are mandatory to be mentioned in your Identity Card.</p>
                                        <table style="width:100%">
                                            <tr>
                                            <td>Blood Group</td>
                                            <td><p>""" + str(emp.employee_id.blood_group or '-')+ """</p></td>
                                            </tr>
                                            <tr>
                                            <td>Emergency Contact Number</td>
                                            <td><p>""" +  str(emp.employee_id.emergency_contact or '-') + """</p></td>
                                            </tr>
                                            </table>                                  
                            <p>A welcome lunch for you will be arranged by us on your joining day. </p>
                            <p>Please revert to this mail in case you have any query or call us on 02246134622/NEO Mobile number</p>       
                            <p>Enclosed: Bank Detail Form & NEO Booklet</p>       
        
        
                                </body>
                                        """
            email_vals_seven = {
                'subject': """Joinee Mail""",
                # 'email_from': 'onboarding@walplast.com',
                'email_to': emp.employee_id.work_email,
                'body_html': message,
            }
            email_seven = self.env['mail.mail'].sudo().create(email_vals_seven)
            email_seven.sudo().send()

        for emp in orient_list_one:
            message_one_day = """<head>
                                                                                <style>
                                                                    table, th, td {
                                                                      border: 1px solid black;
                                                                      border-collapse: collapse;
                                                                    }
                                                                    th, td {
                                                                      padding: 5px;
                                                                    }
                                                                    th {
                                                                      text-align: left;
                                                                    }
                                                                    </style>
                        </head>
                        <body>
                        <p>Dear Mr./Ms.  """ + emp.employee_id.name + """,</p>
                        <p>Only a day to go to start working together!!  As a process, you will soon get a welcome call from your buddy Mr./Ms. and from our EL club member Mr. /Ms.To ensure smooth joining process, request you to refer to your offer letter for documents that you need to carry.</p>
                                                                                          <p>  <table style="width:100%">
                                                        <tr>
                                                        <td>DOJ</td>
                                                        <td>""" + str(emp.date) + """</td>
                                                        </tr>
                                                        <tr>
                                                        <td>Reporting Time</td>
                                                        <td>""" + str(emp.delivery_time) + """</td>
                                                        </tr>
                                                        
                                                        <tr>
                                                        <td>Address</td>
                                                        <td><p>""" + str(company_list.street or '-') + """</p></td>
                                                        </tr>
                                                        
                                                        <tr>
                                                        <td>Reporting Manager name and Contact Number</td>
                                                        <td><p>""" + str(emp.employee_id.parent_id.name or '-') + """ </p>
                                                         <p>""" + str(emp.employee_id.parent_id.work_phone or '-')+ """</p></td>
                                                        </tr>
                                                        
                                                        <tr>
                                                        <td>TEAM NEO contact number</td>
                                                        <td>""" + company_list.phone + """</td>
                                                        </tr>
                                                        <tr>
                                                        <td>Dress Code</td>
                                                        <td>Formal Dress</td>
                                                        </tr>
                                                         </table></p>
                                                         <h4><b>IN CASE NOT PROVIDED BELOW DETAILS</b></h4>
                                                         <p>Share your HDFC salary A/C details like- Account Number, Account Holders Name, IFSC Code, MICR Code, Address along with cancelled HDFC cheque scan copy and also share soft copy of your &amp;photograph. </p>
                                                         <p>In case you do not have Account in HDFC Bank provide us your nearest HDFC Bank details in the attached format only.</p>
                                                         <p>Also, provide the below details asked in the table format. These details are mandatory to be mentioned in your Identity Card.</p>
                                                    <table style="width:100%">
                                                        <tr>
                                                        <td>Blood Group</td>
                                                        <td><p>""" + str(emp.employee_id.blood_group or '-')+ """</p></td>
                                                        </tr>
                                                        <tr>
                                                        <td>Emergency Contact Number</td>
                                                        <td><p>""" +  str(emp.employee_id.emergency_contact or '-') + """</p></td>
                                                        </tr>
                                                        </table>                                  
                                        <p>Here's what you can expect on Day 1
                                        <br/>Joining formalities
                                        <br/>Orientation with HR
                                        <br/>Lunch (provided by us)
                                        <br/><br/>Please revert to this mail in case you have any query or call us on 02246134622/NEO Mobile number
            </p>       
                    
                    
                                            </body>
                                                    """

            # alert_mail = self.env['res.config.settings'].search([], order='id desc', limit=1)

            email_vals_one = {
                'subject': """Joinee Mail""",
                # 'email_from': 'onboarding@walplast.com',
                'email_to': emp.employee_id.work_email,
                'body_html': message_one_day,
            }
            email_one = self.env['mail.mail'].sudo().create(email_vals_one)
            email_one.sudo().send()
            # emp.active_flag=True