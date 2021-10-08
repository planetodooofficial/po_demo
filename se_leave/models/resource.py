from odoo import api, fields, models, _

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.constrains('attendance_ids')
    def _check_attendance(self):
        pass