from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import base64


class MyApproveMessageWizard(models.TransientModel):
    _name = 'approve.message.wizard'
    _description = "Show Message"

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}