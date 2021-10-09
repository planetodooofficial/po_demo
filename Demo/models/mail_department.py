from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
from datetime import date, datetime
from datetime import timedelta


class Mail_department(models.Model):
    _inherit = 'employee.orientation'

    def alert_mail_dept(self):
        today = date.today()
        orient_list_seven = self.env['employee.orientation'].search([('sevenday_mail', '=', today)])

        orient_list_one = self.env['employee.orientation'].search([('oneday_mail', '=', today)])
        # employee_test = self.env['employee.orientation'].search(['id','=', self.id])
        # employe_list = self.env['hr.employee'].search([('id', '=', orient_list.employee_id.id)])
        # employe_list = self.env['hr.employee'].search([('id', '=', orient_list.employee_id.id)])
        company_list = self.env['res.partner'].search([('is_company', '=', True)])
        dept_list = self.env['hr.employee'].search([('department_id.name', '=', 'IT')])
        for emp in orient_list_seven:
            for dept in dept_list:
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
                <p>Dear """ + dept.name + """,</p>
                <p>""" + emp.employee_id.name + """ will join us on """ + str(emp.date) + """,</p>
                <p>Below are details</p>
                            <p> 
                             <table style="width:100%">
                                            <tr>
                                            <td>Dept</td>
                                            <td>""" + str(emp.department_id.name or '-') + """</td>
                                            </tr>
                                            <tr>
                                            <td>Location</td>
                                            <td>""" + str(emp.employee_id.work_location or '-') + """</td>
                                            </tr>
                                            
                                            <tr>
                                            <td>Company</td>
                                            <td><p>""" + str(company_list.name or '-') + """</p></td>
                                            </tr>
                                            </table>
                                            </p>
                                            <p>
                            Request you to create email if on the day of joining. </p>
                            <p><b>           
                           Note-  issue <laptop/desktop> /access card for him/her as per lockdown guidelines.  </p></b> 
                        
                                    </body>
                                            """
                email_vals_seven = {
                    'subject': """New Joinee IT Requirement_""" + emp.employee_id.name + """.""",
                    # 'email_from': 'onboarding@walplast.com',
                    'email_to': dept.work_email,
                    'body_html': message,
                }
                email_seven = self.env['mail.mail'].sudo().create(email_vals_seven)
                email_seven.sudo().send()
        for emp in orient_list_one:
            for dept in dept_list:
                message_one_day = """ <body>
                                   <p>Dear,</p>
                                   <p> """ + emp.employee_id.name + """ will join us on """ +  str(emp.date) + """, as per trail mail create email ID. </p>
                                   
                                                       </body>
                                                               """

                email_vals_one = {
                    'subject': """New Joinee IT Requirement_""" + emp.employee_id.name + """.""",
                    # 'email_from': 'onboarding@walplast.com',
                    # 'email_to': emp.employee_id.work_email,
                    'email_to': dept.work_email,
                    'body_html': message_one_day,
                }
                email_one = self.env['mail.mail'].sudo().create(email_vals_one)
                email_one.sudo().send()


class Mail_Resignation(models.Model):
    _inherit = 'hr.resignation'

    # @api.onchange('employee_id')
    # def _onchange_joining_date(self):
    #     # Force the recompute
    #     extract_date = datetime.strftime(self.employee_id.join_date, "%m/%d/%Y")
    #     into_date = datetime.strptime(extract_date, '%m/%d/%Y')
    #     self.joined_date = into_date

    def confirm_resignation(self):
        res = super(Mail_Resignation, self).confirm_resignation()
        message = """ <body>
        <p>Dear """ + self.employee_id.parent_id.name + """,</p>
        <p>Please accept this message as my formal resignation.Family circumstances currently require my full time and attention.</p>

            <p>Please let me know how I can be of assistance during this transition.</p>

            <p>I am so grateful for my five years at this company, and will look back fondly on the support and kindness I received from management and colleagues.</p>
                            </body>
                                    """
        email_vals_seven = {
            'subject': """Resignation Mail to manager""",
            # 'email_to': 'shivani@planet-odoo.com',
            'email_to': self.employee_id.parent_id.work_email,
            'body_html': message,
        }
        email_seven = self.env['mail.mail'].sudo().create(email_vals_seven)
        email_seven.sudo().send()
        collect_settlement = self.env['hr.employee'].search([('department_id.name', '=', 'Settlement')])
        for emps in collect_settlement:
            message_settlement = """<body>
            <p>Dear """ + emps.name + """,</p>
            <p>Please accept this message as my formal resignation.Family circumstances currently require my full time and attention.</p>

                <p>Please let me know how I can be of assistance during this transition.</p>
                <p>Below are details:
                <ul>
                <li>Resignation:""" + str(self.state) + """</li>
                <li>Type of Resignation:""" + str(self.resignation_type) + """</li>
                <li>Type of Resignation:""" + str(self.expected_revealing_date) + """</li>
                </ul></p>

                <p>I am so grateful for my five years at this company, and will look back fondly on the support and kindness I received from management and colleagues.</p>
                                </body>
                                        """
            email_vals_settlement = {
                'subject': """Resignation Mail to Settlement team""",
                'email_to': emps.work_email,
                # 'email_to': 'shivani@planet-odoo.com',
                'body_html': message_settlement,
            }
            email_settlement = self.env['mail.mail'].sudo().create(email_vals_settlement)
            email_settlement.sudo().send()
        return res

    def approve_resignation(self):
        res = super(Mail_Resignation, self).approve_resignation()
        collect_settlement = self.env['hr.employee'].search([('department_id.name', '=', 'Settlement')])

        for emps in collect_settlement:
            message_settlement = """<body>
            <p>Dear """ + emps.name + """,</p>
            <p>Please accept this message as my formal resignation.Family circumstances currently require my full time and attention.</p>

                <p>Please let me know how I can be of assistance during this transition.</p>
                <p>Below are details:
                <ul>
                <li>Resignation:""" + str(self.state) + """</li>
                <li>Type of Resignation:""" + str(self.resignation_type) + """</li>
                <li>Type of Resignation:""" + str(self.expected_revealing_date) + """</li>
                </ul></p>

                <p>I am so grateful to this company, and will look back fondly on the support and kindness I received from management and colleagues.</p>
                                </body>
                                        """
            email_vals_settlement = {
                'subject': """Resignation Mail to Settlement team for approval""",
                'email_to': emps.work_email,
                # 'email_to': 'shivani@planet-odoo.com',
                'body_html': message_settlement,
            }
            email_settlement = self.env['mail.mail'].sudo().create(email_vals_settlement)
            email_settlement.sudo().send()
        return res

    def reminder_resignation_manager(self):
        message = """ <body>
                <p>Dear """ + self.employee_id.parent_id.name + """,</p>
                <p>I would like to remind you regarding my resignation.
                    And I am kindly requesting you to do the needful.
                                        </p>

                                      </body>
                                            """
        email_vals_manager = {
            'subject': """Resignation Mail Reminder to manager""",
            # 'email_to': 'shivani@planet-odoo.com',
            'email_to': self.employee_id.parent_id.work_email,
            'body_html': message,
        }
        email_seven = self.env['mail.mail'].sudo().create(email_vals_manager)
        email_seven.sudo().send()

    def reminder_resignation_bhr(self):
        collect_bhr = self.env['hr.employee'].search([('department_id.name', '=', 'BHR')])
        for emps in collect_bhr:
            message_bhr = """<body>
                    <p>Dear """ + emps.name + """,</p>
                <p>I would like to remind you regarding my resignation.
                    And I am kindly requesting you to do the needful.
                                        </p>                                       </body>
                                               """
            email_vals_bhr = {
                'subject': """Resignation Mail to BHR team for approval""",
                'email_to': emps.work_email,
                # 'email_to': 'shivani@planet-odoo.com',
                'body_html': message_bhr,
            }
            email_bhr = self.env['mail.mail'].sudo().create(email_vals_bhr)
            email_bhr.sudo().send()
