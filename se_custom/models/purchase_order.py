from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, time
from datetime import date, timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    vendor_user_id = fields.Many2one('res.users',string="Share To")
    pan_no = fields.Char(related='partner_id.pan_no', string="Pan No")
    msme = fields.Char(related='partner_id.msme', string="MSME")
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            today = datetime.today()
            current_month = datetime.strftime(today,'%m')
            current_year = datetime.strftime(today,'%y')
            fiscal =""
            if int(current_month) < 4:
               # prev_year = today - timedelta(days=365)
               # fiscal1 = fiscal1 + datetime.strftime(prev_year, '%Y')
               fiscal = str(int(current_year)-1) + "-" + current_year
            if int(current_month) > 4:
                # comming_year = today + timedelta(days=365)
                # fiscal1 = fiscal1 + datetime.strftime(comming_year, '%Y')
                fiscal = current_year +"-"+str(int(current_year) + 1)

            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            seq = self.env['ir.sequence'].next_by_code('custom.purchase.order', sequence_date=seq_date)
            vals['name'] = "SEPO/"+ fiscal +"/"+seq or '/'
        return super(PurchaseOrder, self).create(vals)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vendor_user_id = fields.Many2one(related='order_id.vendor_user_id')