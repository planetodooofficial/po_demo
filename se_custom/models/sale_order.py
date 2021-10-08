from odoo import api, fields, models, _,tools
from datetime import datetime, date
from odoo.exceptions import UserError
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class SalesMilestone(models.Model):
    _name = 'sales.milestone'

    sale_ref = fields.Many2one('sale.order')
    seq = fields.Integer("Sr. No.")
    milestone_perc = fields.Float(string="Milestone")
    description = fields.Char("Description")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cust_user_id = fields.Many2one('res.users',string="Share To")
    so_desc = fields.Text(string="SO Description",compute='_onchange_product')
    pan_no = fields.Char(related='partner_id.pan_no',string="Pan No")
    msme = fields.Char(related='partner_id.msme',string="MSME")
    project_type = fields.Selection([('grc', 'GRC'), ('testing', 'Testing'), ('comprehensive', 'Comprehensive'), ('mandays_project','Mandays project'), ('internal', 'Internal')],String="Project Type")
    project_type_code = fields.Char(String="Project code")
    po_desc = fields.Char(string="PO Number")

    @api.depends('partner_id','order_line.product_id')
    def _onchange_product(self):
        code = ""
        if self.partner_id or self.order_line or self.order_line.product_id:
            code += self.partner_id.partner_code or ""
            count = 0
            for rec in self.order_line:
                order_id = rec.product_id.product_code
                if count == 0:
                    if order_id:
                        code += '/' + str(order_id)
                    count += 1
                else:
                    code += '-' + str(order_id)
        self.so_desc = code
        # self.write({'so_desc': code})

    @api.depends('amount_untaxed')
    def compute_custom_amount_untaxed(self):
        if self.amount_untaxed:
            self.custom_amount_untaxed = self.amount_untaxed * self.partner_id.custom_currency_id.rate
        else:
            self.custom_amount_untaxed = self.amount_untaxed

    @api.depends('amount_tax')
    def compute_custom_amount_tax(self):
        if self.amount_tax:
            self.custom_amount_tax = self.amount_tax * self.partner_id.custom_currency_id.rate
        else:
            self.custom_amount_tax = self.amount_tax

    @api.depends('amount_total')
    def compute_custom_amount_total(self):
        if self.amount_total:
            self.custom_amount_total = self.amount_total * self.partner_id.custom_currency_id.rate
        else:
            self.custom_amount_total = self.amount_total

    deliverable = fields.Text("Deliverables")
    project_template = fields.Many2one('project.project',string="Sub Project",domain="[('is_a_template','=',True)]")
    sale_milestone = fields.One2many('sales.milestone','sale_ref',string="Milestones")
    tot_per = fields.Float("Total milestone:",compute="compute_total_percent")
    amount_to_pay = fields.Float("Milestone based amount:",compute="compute_milestone_amount")
    custom_amount_untaxed = fields.Monetary(compute='compute_custom_amount_untaxed')
    custom_amount_tax = fields.Monetary(compute='compute_custom_amount_tax')
    custom_amount_total = fields.Monetary(compute='compute_custom_amount_total')

    @api.depends('tot_per')
    def compute_milestone_amount(self):
        if self.tot_per:
            self.amount_to_pay = (self.amount_total/100)*self.tot_per
        else:
            self.amount_to_pay = 0.0

    @api.depends('sale_milestone')
    def compute_total_percent(self):
        if self.sale_milestone:
            for milestone in self.sale_milestone:
                    self.tot_per += (milestone.milestone_perc)*100
        else:
            self.tot_per=0.0

    @api.onchange('sale_milestone')
    def compute_serial_number(self):
        seq=0
        for milestone in self.sale_milestone:
            milestone.seq = seq+1
            seq +=1

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount'] * self.partner_id.custom_currency_id.rate
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if self.project_ids:
            for project in self.project_ids:
                tasks = self.env['project.task'].search([('project_id','=',project.id)])
                for task in tasks:
                    task.write({'sale_line_id':False})
                tasks.unlink()
                project.unlink()
                # for task in tasks:

                # self.env.cr.execute("delete from project_task where project_id=%s", [project.id,])
                # self.env.cr.execute("delete from project_project where id=%s", [project.id,])
        return res


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if not self.po_desc:
            raise UserError(_('PO Number is required to confirm the Quotation!!'))
        if not self.partner_id.vat:
            raise UserError(_('Please Enter GST No.'))
        return res

    @api.onchange('project_type')
    def _onchange_proj_types(self):
        if self.project_type:
            if self.project_type == 'grc':
                self.project_type_code = 'GRC'
            elif self.project_type == 'testing':
                self.project_type_code = 'TEST'
            elif self.project_type == 'comprehensive':
                self.project_type_code = 'COMP'
            elif self.project_type == 'mandays_project':
                self.project_type_code = 'Mandays project'
            elif self.project_type == 'internal':
                self.project_type_code = 'INT'
        else:
            pass


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('price_unit')
    def compute_custom_price_unit(self):
        for rec in self:
            if rec.price_unit:
                rec.custom_price_unit = rec.price_unit * rec.order_id.partner_id.custom_currency_id.rate
            else:
                rec.custom_price_unit = rec.price_unit

    @api.depends('price_subtotal')
    def compute_custom_price_subtotal(self):
        for rec in self:
            if rec.price_subtotal:
                rec.custom_price_subtotal = rec.price_subtotal * rec.order_id.partner_id.custom_currency_id.rate
            else:
                rec.custom_price_subtotal = rec.price_subtotal

    @api.depends('price_tax')
    def compute_custom_price_tax(self):
        if self.price_tax:
            self.custom_price_tax = self.price_tax * self.order_id.partner_id.custom_currency_id.rate
        else:
            self.custom_price_tax = self.price_tax

    @api.depends('price_total')
    def compute_custom_price_total(self):
        if self.price_total:
            self.custom_price_total = self.price_total * self.order_id.partner_id.custom_currency_id.rate
        else:
            self.custom_price_total = self.price_total

    department_id = fields.Many2one('hr.department',string="Department")
    custom_price_unit = fields.Float(compute='compute_custom_price_unit')
    custom_price_subtotal = fields.Monetary(compute='compute_custom_price_subtotal')
    custom_price_tax = fields.Float(compute='compute_custom_price_tax')
    custom_price_total = fields.Monetary(compute='compute_custom_price_total')

    @api.onchange('product_id')
    def _onchange_product(self):
        self.department_id = self.product_id.department

    def _timesheet_create_project(self):
        """ Generate project for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        self.ensure_one()
        values = self._timesheet_create_project_prepare_values()
        if self.product_id.project_template_id:
            # values['name'] = self.env['ir.sequence'].next_by_code('project.project')
            project = self.product_id.project_template_id.copy(values)
            project.tasks.write({
                'sale_line_id': self.id,
                'partner_id': self.order_id.partner_id.id,
                'email_from': self.order_id.partner_id.email,
            })
            # duplicating a project doesn't set the SO on sub-tasks
            project.tasks.filtered(lambda task: task.parent_id != False).write({
                'sale_line_id': self.id,
            })
        else:
            project = self.env['project.project'].create(values)

        # Avoid new tasks to go to 'Undefined Stage'
        if not project.type_ids:
            if self.order_id.project_template:
                project.type_ids = [(6, 0, self.order_id.project_template.type_ids.ids)]
            else:
                project.type_ids = self.env['project.task.type'].create({'name': _('New')})

        # link project as generated by current so line
        self.write({'project_id': project.id})
        return project

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
            account = self.order_id.analytic_account_id

        # create the project or duplicate one
        return {
            # 'name': self.env['ir.sequence'].next_by_code('project.project'),
            'analytic_account_id': account.id,
            'partner_id': self.order_id.partner_id.id,
            'so_desc': self.order_id.so_desc,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'active': True,
            'company_id': self.company_id.id,
        }


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # def create_invoices(self):
    #     sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
    #     for sale in sale_orders:
    #         for line in sale.order_line:
    #             if line.task_id:
    #                 if line.task_id.stage_id.id == line.task_id.project_id.final_stage.id and line.task_id.kanban_state == 'done':
    #                     continue
    #                 else:
    #                     raise UserError(_('Please complete the milestone first to create an invoice!!'))
    #     if self.advance_payment_method == 'delivered':
    #         sale_orders._create_invoices(final=self.deduct_down_payments)
    #     else:
    #         # Create deposit product if necessary
    #         if not self.product_id:
    #             vals = self._prepare_deposit_product()
    #             self.product_id = self.env['product.product'].create(vals)
    #             self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
    #
    #         sale_line_obj = self.env['sale.order.line']
    #         for order in sale_orders:
    #             amount, name = self._get_advance_details(order)
    #
    #             if self.product_id.invoice_policy != 'order':
    #                 raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
    #             if self.product_id.type != 'service':
    #                 raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
    #             taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
    #             tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
    #             context = {'lang': order.partner_id.lang}
    #             analytic_tag_ids = []
    #             for line in order.order_line:
    #                 analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    #
    #             so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
    #             so_line = sale_line_obj.create(so_line_values)
    #             del context
    #             self._create_invoice(order, so_line, amount)
    #     if self._context.get('open_invoices', False):
    #         return sale_orders.action_view_invoice()
    #     return {'type': 'ir.actions.act_window_close'}