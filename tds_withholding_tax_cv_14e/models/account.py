# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tds = fields.Boolean('TDS', default=False)
    payment_excess = fields.Float('Payment in excess of')
    tds_applicable = fields.Selection([('person', 'Individual'),
                                       ('company', 'Company'),
                                       ('common', 'Common')], string='Applicable to')
