from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
import fiscalyear


class ObjectivetMaster(models.Model):
    _name = 'objective.master'
    _rec_name = 'objective_name'

    objective_name = fields.Char(string="Objective Name")
    key_skill_many = fields.Many2many('key.results', string="Key Results",required=True)
    role_mapping_id = fields.Many2one('role.mapping', string="Roles Name")
    objective_weight = fields.Float(string="Objective Weightage")


class Keyskills(models.Model):
    _name = 'key.results'
    _rec_name = 'key_skills'

    key_skills = fields.Char(string="Key Results")


class ValuesMaster(models.Model):
    _name = 'value.master'
    _rec_name = 'values_store'

    values_store = fields.Char(string="Values")
    value_weight = fields.Float(string="Values Weightage")


class QuarterMaster(models.Model):
    _name = 'quarter.master'

    name = fields.Integer(string="Quarter")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date to")
    # year = fields.Integer(string="Year")

    years = fields.Char(string="Year")

    def quarter_assign(self):
        previous_date = 0
        fiscalyear.START_MONTH = 4
        start_date = fiscalyear.FiscalYear(datetime.now().year + 1).start.date()
        year = str(start_date.year) + "-"+str(start_date.year + 1)
        checkouts = self.env['quarter.master'].search([('years', '=', year)])
        if not checkouts:
            for i in range(1, 5):
                if i == 1:
                    emp = {
                        'name': i,
                        'date_from': start_date,
                        'date_to': start_date + relativedelta(months=+3) + timedelta(days=-1),
                        'years': year
                    }
                    new_emp = self.env['quarter.master'].sudo().create(emp)
                    previous_date = emp['date_to'] + timedelta(days=+1)
                else:
                    emp = {
                        'name': i,
                        'date_from': previous_date,
                        'date_to': previous_date + relativedelta(months=+3) + timedelta(days=-1),
                        'years': year
                    }
                    new_emp = self.env['quarter.master'].sudo().create(emp)
                    previous_date = emp['date_to'] + timedelta(days=+1)
                print(checkouts)
        else:
             print(checkouts)

    # @api.onchange('date_from')
    # def onchange_date_start(self):
    #     self.year = 2016
    #
    #     if self.date_from :
    #          self.date_to = self.date_from + relativedelta(months=+3) + timedelta(days=-1)
