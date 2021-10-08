# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id','tds_tax_id')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self:
            move.total_gross = move.amount_untaxed
            move.tds_amt = -(move.tds_tax_id.amount * (move.total_gross / 100))
            move.amount_total = move.amount_untaxed + move.amount_tax + move.tds_amt
            applicable = True
            if move.partner_id and move.partner_id.tds_threshold_check and move.tds_tax_id:
                applicable = move.check_turnover(move.partner_id.id, move.tds_tax_id.payment_excess,
                                                 move.total_gross)
            if not applicable:
                move.tds_amt = 0
        return res

    tds = fields.Boolean('Apply TDS', default=False, readonly=True,
                         states={'draft': [('readonly', False)]})
    tds_tax_id = fields.Many2one('account.tax', string='TDS',
                                 states={'draft': [('readonly', False)]})
    tds_amt = fields.Monetary(string='TDS Amount',
                              store=True, readonly=True, compute='_compute_amount')
    total_gross = fields.Monetary(string='Total',
                                  store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Net Total',
                                   store=True, readonly=True, compute='_compute_amount')
    vendor_type = fields.Selection(related='partner_id.company_type', string='Partner Type')


    def _post(self, soft=True):
        if self.tds_tax_id:
            # self.amount_total = self.amount_total - self.tds_amt
            # self.amount_residual = self.amount_residual - self.tds_amt
            move = self.env['account.move'].create({
                'move_type': 'entry',
            })
            tax_repartition_lines = self.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax') if self.tds_tax_id else None
            total_gross = self.amount_untaxed
            tds_amt = self.tds_tax_id.amount * (total_gross / 100)

            move.line_ids = [
                    (0,0, {
                        'debit': tds_amt if self.move_type == 'out_invoice' else 0,
                        'credit': 0 if self.move_type == 'out_invoice' else tds_amt,
                        'partner_id': self.partner_id.id,
                        'account_id': self.partner_id.property_account_receivable_id.id if self.move_type == 'out_invoice' else self.partner_id.property_account_payable_id.id
                    }),

                    (0,0, {
                        'debit': 0 if self.move_type == 'out_invoice' else tds_amt,
                        'credit': tds_amt if self.move_type == 'out_invoice' else 0,
                        'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id
                    }),
                ]
            move.action_post()

        return super(AccountMove, self)._post(soft=True)

    def check_turnover(self, partner_id, threshold, total_gross):
        domain = [('partner_id', '=', partner_id), ('account_id.internal_type', '=', 'payable'),
                  ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
        journal_items = self.env['account.move.line'].search(domain)
        credits = sum([item.credit for item in journal_items])
        credits += total_gross
        if credits >= threshold:
            return True
        else:
            return False

    @api.onchange('tds_tax_id', 'tds')
    def _onchange_tds_tax_id(self):
        for invoice in self:
            applicable = True
            if invoice.partner_id and invoice.partner_id.tds_threshold_check:
                applicable = invoice.check_turnover(invoice.partner_id.id, invoice.tds_tax_id.payment_excess,
                                                    invoice.total_gross)
            tax_repartition_lines = invoice.tds_tax_id.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == 'tax') if invoice.tds_tax_id else None
            existing_line = invoice.line_ids.filtered(
                lambda x: x.account_id.id == tax_repartition_lines.account_id.id) if tax_repartition_lines else None
            tds_amount = abs(invoice.tds_amt) if invoice.tds and applicable else 0
            tds_tax = invoice.tds_tax_id if invoice.tds_tax_id else None
            credit = 0
            debit = 0
            if invoice.move_type in ['in_invoice']:
                credit = tds_amount
            elif invoice.move_type in ['out_invoice']:
                debit = tds_amount
            if applicable and tds_amount and tds_tax and tax_repartition_lines:
                if existing_line:
                    existing_line.credit = credit
                    existing_line.debit = debit
                else:
                    create_method = invoice.env['account.move.line'].new
                    create_method({
                        'name': tds_tax.name,
                        'debit': debit,
                        'credit': credit,
                        'quantity': 1.0,
                        'amount_currency': tds_amount,
                        'date_maturity': invoice.invoice_date,
                        'move_id': invoice.id,
                        'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                        'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                        'partner_id': invoice.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                invoice._onchange_recompute_dynamic_lines()
            elif existing_line:
                existing_line.credit = 0
                invoice._onchange_recompute_dynamic_lines()
                invoice.line_ids -= existing_line


class AccountInvoiceTax(models.Model):
    _inherit = "account.tax"

    tds = fields.Boolean('TDS', default=False)
