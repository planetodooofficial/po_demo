from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
import datetime


class ConfirmQuotation(models.TransientModel):
    _name = 'quotation.master'

    no_days = fields.Integer(string='No of days')
    project_manager = fields.Many2one("res.users", string="Project Manager")

    # def (self):
    #     active_id = self.env.context.get('active_id')
    #

    def action_confirm(self):
        active_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        active_id.action_confirm()
        collect_product = ''
        if active_id.project_ids:
            for projects in active_id.project_ids:
                projects.user_id = self.project_manager.id
                if projects.user_id:
                    for rec in active_id.order_line:
                        collect_product += rec.product_id.name + ','
                    message = """
                                                                 <p>Dear """ + projects.user_id.name + """</p>
                                                                 <p>Kindly note that we have received a new purchase order. Please find the details below:</p>
                                                                 <p>Customer name:  """ + active_id.partner_id.name + """ </p>
                                                                 <p>Type of Activity:  """ + collect_product + """ </p>
                                                                 <p>Estimated number of days::  """ + str(self.no_days) + """ </p>
                      
                                                                """
                    if active_id.partner_id.phone:
                        message += """
                                         <p>Contact details:
                                          <br/>Contact No. """ + str(active_id.partner_id.phone) + """</p>
                                                                    <p>Email ID: """ + active_id.partner_id.email if active_id.partner_id.email else '' + """</p>
 """
                    else:
                        message += """<p>Contact details: <br/>
                        Contact No. """ + str(active_id.partner_id.mobile or "-") + """</p>
                                                                    <p>Email ID: """ + active_id.partner_id.email if active_id.partner_id.email else '' + """</p>
"""

                    message += """
                                         <p> 
                                                                 Address: """ + active_id.partner_id.street if active_id.partner_id.street else '' + """
                                                                
                                                                  </p>
                                                                 <br/>

                                                                                             """
                    print(message)
                    email_vals = {
                        'subject': """New Sale Order is created""",
                        'email_to': projects.user_id.login,
                        'body_html': message,
                    }
                    email = self.env['mail.mail'].sudo().create(email_vals)
                    email.sudo().send()
