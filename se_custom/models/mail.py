from odoo import api, fields, models, _,tools
from datetime import datetime, date

class Mail(models.Model):
    _inherit='mail.mail'

    custom_schedule_date = fields.Date(string="Scheduled Date")

    def schedule_send(self):
        mails = self.env['mail.mail'].search([('state','=','outgoing')])
        today = datetime.today()
        for mail in mails:
            if mail.custom_schedule_date and mail.custom_schedule_date == today:
                mail.send()

