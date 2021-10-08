from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
from datetime import date
from datetime import timedelta


class AlertMail(models.Model):
    _inherit = 'sale.order'

    def alert_mail_proposals(self):
        if self.project_ids:
            for projects in self.project_ids:
                if projects.user_id and self.partner_id.mobile or self.partner_id.phone:
                    message = """
                                                                    <p>Dear """ + projects.user_id.name + """</p><br/>
                                                                    <p>New Sale Order  of """ + self.partner_id.name + """ with contact details """ + str(
                        self.partner_id.phone) + """</p>
                                                                    <br/>
    
                                                                                                """
                    email_vals = {
                        'subject': """New Sale Order is created""",
                        'email_to': 'shivani.planetodoo@gmail.com',
                        'body_html': message,
                    }
                    email = self.env['mail.mail'].sudo().create(email_vals)
                    email.sudo().send()

    def alert_mail_expiration(self):
        today = date.today()
        next_five_days = today + timedelta(days=5)
        sale_orders = self.env['sale.order'].search(
            [('submission_date', '>=', today), ('submission_date', '<=', next_five_days)],
            order='submission_date ASC,priority_select')
        print(sale_orders)
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
        <p>Dear All,</p>
        <p>Please find the following proposal submissions due in the next 5 days.</p>
                                                                            <table style="width:100%">
                                                                                      <tr>
                                                                                        <th>Number</th>
                                                                                        <th>Creation Date</th> 
                                                                                        <th>Customer</th>
                                                                                        <th>Salesperson</th>
                                                                                        <th>Submission Date</th>
                                                                                      </tr>"""

        for sale in sale_orders:
            message += """      <tr>
                                        <td>""" + sale.name + """</td>
                                        <td>""" + str(sale.date_order) + """</td>
                                        <td>""" + sale.partner_id.name + """</td>
                                        <td>""" + sale.user_id.name + """</td>
                                        <td>""" + str(sale.submission_date) + """</td>
                                      </tr>
                                    """
        message += """</table>
    
                            </body>
    """
        alert_mail = self.env['res.config.settings'].search([],order='id desc',limit=1)
        print(alert_mail)
        email_vals = {
            'subject': """New Sale Order is created""",
            'email_from': alert_mail.alert_id,
            'email_to': alert_mail.alert_id,
            'body_html': message,
        }
        email = self.env['mail.mail'].sudo().create(email_vals)
        email.sudo().send()


class EmailComposeSale(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        res=super(EmailComposeSale, self).action_send_mail()
        active_model=self.env.context.get('active_model') == 'sale.order'
        active_id = self._context.get('active_id')
        if self.env.context.get('active_model') == 'sale.order' and active_id:
            email_sale=self.env['sale.order'].search([('id', '=', active_id)])
            if email_sale.check_proposal:
                email_sale.state = 'sent'
            else:
                email_sale.state = 'draft'
        pass