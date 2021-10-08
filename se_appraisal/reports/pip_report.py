from odoo import api, models
import datetime

class PipReport(models.AbstractModel):
    """ Model to contain the information related to printing the information about
    the COA report"""

    _name = "report.se_appraisal.template_pip_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get the report values.
                        :param : model
                        :param : docids
                        :param : data
                        :return : data
                        :return : PIP and Meeting data"""
        pip = self.env['pip.bip'].browse(docids)
        meetings = self.env['pip.meeting'].search([('pip_meeting','=',pip.id)])

        return {
            'data': data,
            'docs': pip,
            'meetings':meetings
        }