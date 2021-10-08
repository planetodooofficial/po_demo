from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning

class Survey(models.Model):
    _inherit = 'survey.survey'

    candidate = fields.Many2one('hr.applicant',"Candidate")

    @api.model
    def default_get(self, fields_list):
        res = super(Survey, self).default_get(fields_list)
        if self.env.context.get('active_id'):
            application = self.env['hr.applicant'].search([('id', '=', self.env.context['active_id'])])
            if application:
                res['candidate'] = application.id
        return res
