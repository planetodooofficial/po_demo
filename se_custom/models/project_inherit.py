from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
from datetime import timedelta
import itertools
import json
from odoo.addons.web.controllers.main import clean_action

DEFAULT_MONTH_RANGE = 3

class Project(models.Model):
    _inherit = 'project.project'

    # _sql_constraints = [
    #     ('code_project_uniq', 'unique(name)',
    #      'Project already exist with same name')
    # ]

    @api.depends('sub_proj')
    def _count_sub_projects(self):
        for rec in self:
            if rec.sub_proj:
                rec.sub_proj_count = int(len(rec.sub_proj))
            else:
                rec.sub_proj_count=0

    @api.depends('name')
    def get_current_id(self):
        for rec in self:
            if rec.id:
                rec.current_record = rec.id
            else:
                rec.current_record = False

    @api.depends('sub_proj')
    def compute_sub_projects(self):
        for rec in self:
            if rec.id:
                projects = self.env['project.project'].search([('parent_proj.id', '=', rec.id)]).id
                if projects:
                    rec.sub_proj_count = len(projects)
                    rec.sub_proj_created = True
                else:
                    rec.sub_proj_count = 0
                    rec.sub_proj_created = False

    name = fields.Char("Name", default="New",index=True,tracking=True,required=False)
    project_name = fields.Char("Project Name",compute="compute_name_projects")
    is_a_template = fields.Boolean("Is a template")
    is_name_check = fields.Boolean("Is a Name")
    project_template = fields.Many2one('project.project',string="Template",domain="[('is_a_template','=',True)]")
    proj_ref = fields.Many2one('project.project')
    sub_proj = fields.Many2many('project.project','proj_ref','project_sub_project_rel',string="Sub Projects")
    parent_proj =  fields.Many2one('project.project',help="To refer the parent project")
    sub_proj_count = fields.Integer(compute='_count_sub_projects',string="Sub Projects")
    current_record = fields.Integer(compute='get_current_id')
    project_status = fields.Selection([('new', 'New'), ('assigned', 'Assigned'), ('process', 'In Process'), ('paused','Paused'), ('closed', 'Closed and Locked')],default='new')
    # final_stage = fields.Many2one('project.task.type',string="Final Stage",store=True, domain="[('id','in',type_ids)]")
    so_desc = fields.Text("Project Description")
    sub_project_count = fields.Char(compute='compute_sub_projects')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('locked', 'Locked'),
    ], string='Project Status',default='draft')
    sub_proj_created = fields.Boolean(compute='compute_sub_projects',store=True)

    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users'),
        ('employees', 'All internal users'),
        ('portal', 'Invited portal users and all internal users'),
    ],
        string='Visibility', required=True,
        default='followers',
        help="Defines the visibility of the tasks of the project:\n"
             "- Invited internal users: employees may only see the followed project and tasks.\n"
             "- All internal users: employees may see all project and tasks.\n"
             "- Invited portal and all internal users: employees may see everything."
             "   Portal users may see project and tasks followed by\n"
             "   them or by someone of their company.")

    @api.onchange('project_status')
    def set_project_status(self):
        for rec in self:
            if rec.project_status == 'closed':
                if rec.parent_proj:
                    for task in rec.task_ids:
                        if task.kanban_state != 'done':
                            raise UserError(_('Not all the task are in Closed State'))

                    rec.write({'state': 'locked'})

                else:
                    sub_proj_obj = self.env['project.project'].search([('parent_proj','=', self._origin.id)])
                    for sub_proj in sub_proj_obj:
                        if sub_proj.project_status != 'closed':
                            raise UserError(_('Not all the Sub-Projects are in Closed State'))

                    rec.write({'state': 'locked'})

            # if rec.project_status == 'closed':
            #     rec.write({'state': 'locked'})
            else:
                rec.write({'state': 'draft'})

    def create_sub_projects(self):
        if self.sub_proj:
            for proj in self.sub_proj:
                sub_proj_obj = self.env['project.project'].create({
                    'name':str(self.name)+":"+str(proj.name),
                    'type_ids': [(6, 0, proj.type_ids.ids)],
                    'parent_proj':self.id,
                })

                for tasks in proj.task_ids:
                    new_task_obj = tasks.copy({'name': tasks.name,'project_id': sub_proj_obj.id, 'stage_id': tasks.stage_id.id,})
                    sub_proj_obj.write({'task_ids': [(4, 0, new_task_obj.id)],})

                    for attachments in tasks.attachment_ids:
                        attachment_obj = attachments.copy({'res_id': new_task_obj.id,})
                        new_task_obj.write({'attachment_ids': [(4, 0, attachment_obj.id)],})

            self.sub_proj_created = True

    @api.model
    def create(self,vals):
        res = super(Project, self).create(vals)
        # if not res.name:
        if not res.is_a_template and 'New' in res.name:
            res['name'] = self.env['ir.sequence'].next_by_code('project.project')
        if res.project_template:
            res.update({'type_ids':[(6, 0, res.project_template.type_ids.ids)]})
        return res

    def action_view_sub_projects(self):

        user_id = self.env.user
        project_admin = user_id.has_group('project.group_project_manager')
        active_id= self.id
        action = {}
        for rec in self:
            if rec.sub_proj_created:
                action = rec.with_context(active_id=rec.id, active_ids=rec.ids) \
                    .env.ref('se_custom.open_view_project_all_copy') \
                    .sudo().read()[0]
                action['display_name'] = rec.name
                action['domain'] = [('parent_proj.id','=',rec.id)]
            else:
                action = rec.with_context(active_id=rec.id, active_ids=rec.ids) \
                    .env.ref('project.act_project_project_2_project_task_all') \
                    .sudo().read()[0]
                action['display_name'] = rec.name

                if not project_admin:
                    action['domain'] = [('user_id','=',user_id.id), ('project_id', '=', active_id)]

        return action


    def _plan_get_stat_button(self):
        stat_buttons = []
        num_projects = self.env['project.project'].search([('id', 'in', self.ids),('parent_proj','=',False)])

        if len(num_projects) == 1:
            proj_action_data = _to_action_data('project.project', res_id=num_projects.id,
                                          views=[[self.env.ref('project.edit_project').id, 'form']])
        else:
            proj_action_data = _to_action_data(action=self.env.ref('project.open_view_project_all_config'),
                                          domain=[('id', 'in', num_projects.ids),('parent_proj','=',False)])

        stat_buttons.append({
            'name': _('Project') if num_projects == 1 else _('Projects'),
            'count': len(num_projects),
            'icon': 'fa fa-puzzle-piece',
            'action': proj_action_data
        })


        # stat for related sub_projects
        sub_projects = self.env['project.project'].search([('parent_proj.id','in',num_projects.ids)])

        sub_proj_action_data = _to_action_data(action=self.env.ref('project.open_view_project_all_config'),
                                      domain=[('parent_proj.id', 'in', num_projects.ids)])

        stat_buttons.append({
            'name': _('Sub Project') if len(sub_projects) == 1 else _('Sub Projects'),
            'count': len(sub_projects),
            'icon': 'fa fa-puzzle-piece',
            'action': sub_proj_action_data
        })

        # if only one project, add it in the context as default value
        tasks_domain = [('project_id', 'in', num_projects.ids)]
        tasks_context = self.env.context.copy()
        tasks_context.pop('search_default_name', False)
        late_tasks_domain = [('project_id', 'in', num_projects.ids), ('date_deadline', '<', fields.Date.to_string(fields.Date.today())), ('date_end', '=', False)]
        overtime_tasks_domain = [('project_id', 'in', num_projects.ids), ('overtime', '>', 0), ('planned_hours', '>', 0)]


        # filter out all the projects that have no tasks
        task_projects_ids = self.env['project.task'].read_group([('project_id', 'in', sub_projects.ids)], ['project_id'], ['project_id'])
        task_projects_ids = [p['project_id'][0] for p in task_projects_ids]

        if len(task_projects_ids) == 1:
            tasks_context = {**tasks_context, 'default_project_id': task_projects_ids[0]}
        stat_buttons.append({
            'name': _('Tasks In Sub-Projects'),
            'count': sum(self.mapped('task_count')),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=tasks_domain,
                context=tasks_context
            )
        })

        stat_buttons.append({
            'name': [_("Tasks"), _("Late")],
            'count': self.env['project.task'].search_count(late_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=late_tasks_domain,
                context=tasks_context,
            ),
        })
        stat_buttons.append({
            'name': [_("Tasks"), _("in Overtime")],
            'count': self.env['project.task'].search_count(overtime_tasks_domain),
            'icon': 'fa fa-tasks',
            'action': _to_action_data(
                action=self.env.ref('project.action_view_task'),
                domain=overtime_tasks_domain,
                context=tasks_context,
            ),
        })

        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            # read all the sale orders linked to the projects' tasks
            task_so_ids = self.env['project.task'].search_read([
                ('project_id', 'in', num_projects.ids), ('sale_order_id', '!=', False)
            ], ['sale_order_id'])
            task_so_ids = [o['sale_order_id'][0] for o in task_so_ids]

            sale_orders = self.mapped('sale_line_id.order_id') | self.env['sale.order'].browse(task_so_ids)
            if sale_orders:
                stat_buttons.append({
                    'name': _('Sales Orders'),
                    'count': len(sale_orders),
                    'icon': 'fa fa-dollar',
                    'action': _to_action_data(
                        action=self.env.ref('sale.action_orders'),
                        domain=[('id', 'in', sale_orders.ids)],
                        context={'create': False, 'edit': False, 'delete': False}
                    )
                })

                invoice_ids = self.env['sale.order'].search_read([('id', 'in', sale_orders.ids)], ['invoice_ids'])
                invoice_ids = list(itertools.chain(*[i['invoice_ids'] for i in invoice_ids]))
                invoice_ids = self.env['account.move'].search_read([('id', 'in', invoice_ids), ('move_type', '=', 'out_invoice')], ['id'])
                invoice_ids = list(map(lambda x: x['id'], invoice_ids))

                if invoice_ids:
                    stat_buttons.append({
                        'name': _('Invoices'),
                        'count': len(invoice_ids),
                        'icon': 'fa fa-pencil-square-o',
                        'action': _to_action_data(
                            action=self.env.ref('account.action_move_out_invoice_type'),
                            domain=[('id', 'in', invoice_ids), ('move_type', '=', 'out_invoice')],
                            context={'create': False, 'delete': False}
                        )
                    })

        ts_tree = self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        ts_form = self.env.ref('hr_timesheet.hr_timesheet_line_form')
        if self.env.company.timesheet_encode_uom_id == self.env.ref('uom.product_uom_day'):
            timesheet_label = [_('Days'), _('Recorded')]
        else:
            timesheet_label = [_('Hours'), _('Recorded')]

        stat_buttons.append({
            'name': timesheet_label,
            'count': sum(self.mapped('total_timesheet_time')),
            'icon': 'fa fa-calendar',
            'action': _to_action_data(
                'account.analytic.line',
                domain=[('project_id', 'in', num_projects.ids)],
                views=[(ts_tree.id, 'list'), (ts_form.id, 'form')],
            )
        })

        return stat_buttons

    @api.depends('project_name')
    def compute_name_projects(self):
        today = datetime.now()
        for rec in self:
            if rec.sale_order_id and rec.partner_id.partner_code and rec.sale_order_id.project_type_code:
                sale_count = self.env['sale.order'].search_count([('id', '=', rec.sale_order_id.id)])
                rec.is_name_check =True
                rec.project_name=rec.partner_id.partner_code + "-"+ str(today.year)+"-"+rec.sale_order_id.project_type_code+"-"+str(sale_count)
            else:
                rec.is_name_check = False
                rec.project_name=rec.name








def _to_action_data(model=None, *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = clean_action(action.read()[0], env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None:  # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr


class ProjectTaskInherit(models.Model):
    _inherit = "project.task"

    start_date = fields.Date(string='Start Date')
    # kanban_state = fields.Selection(selection_add=[('new', 'New'), ('paused', 'Paused')], ondelete={'new': 'set default', 'paused': 'set default'})

    kanban_state = fields.Selection([
        ('new', 'New'),
        ('normal', 'In Progress'),
        ('blocked', 'Paused'),
        ('complete', 'Complete'),
        ('in_review', 'In Review'),
        ('done', 'Closed')], string='Task State',
        copy=False, default='new', required=True)

    legend_new = fields.Char(related='stage_id.legend_new', string='Kanban New Explanation', readonly=True,
                             related_sudo=False)
    legend_paused = fields.Char(related='stage_id.legend_paused', string='Kanban Paused Explanation', readonly=True,
                                related_sudo=False)

    project_manager_task = fields.Many2one(related='project_id.user_id', string='Project_manager')
    is_user = fields.Boolean("Is a User")


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            elif task.kanban_state == 'new':
                task.kanban_state_label = task.legend_new
            elif task.kanban_state == 'paused':
                task.kanban_state_label = task.legend_paused
            else:
                task.kanban_state_label = task.legend_done



    def utilisation_record(self):
        domain = [('user_id', '=', self.user_id.id),('id', '!=', self.id)]
        # view_id = self.env.ref('hr_timesheet.hr_timesheet_line_tree').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Resource Utilisation'),
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'views': [[False, 'list']],
            # 'view_id': view_id,
            'domain': domain,
        }
        # domain = [('user_id','=', self.user_id.id),('project_id','!=', self.project_id.id)]
        # view_id = self.env.ref('hr_timesheet.hr_timesheet_line_tree').id
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _('Resource Utilisation'),
        #     'res_model': 'account.analytic.line',
        #     'view_mode': 'tree,form,pivot,kanban',
        #     'views': [[view_id, 'list']],
        #     # 'view_id': view_id,
        #     'domain': domain,
        # }

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            elif task.kanban_state == 'done':
                task.kanban_state_label = task.legend_done
            else:
                task.kanban_state_label = task.legend_new

# Commented as new requirement
    @api.depends('planned_hours', 'start_date')
    def _onchange_estimate_deadline(self):
        today = datetime.today()
        store_hours =0
        for rec in self:
            if rec.planned_hours and rec.start_date and rec.user_id:
                average_hrs = 8.0
                non_working_days=0.0
                non_working_days_hours=0.0
                if rec.user_id.employee_id:
                    average_hrs = rec.user_id.employee_id.resource_calendar_id.hours_per_day
                    # working_days=rec.user_id.employee_id.resource_calendar_id.attendance_ids
                    # non_working_days=7.0-len(working_days)
                    # non_working_days_hours=non_working_days*average_hrs

                collect_users=self.env['project.task'].search([('user_id', '=', rec.user_id.id)])
                for res in collect_users:
                    if res.start_date and rec.start_date and res.estimated_deadline:
                        if res.start_date <= rec.start_date <= res.estimated_deadline:
                            store_hours+=res.planned_hours

                weekdays = {}
                one_week_days = []
                even_week_days = []
                odd_week_days = []
                if not rec.user_id.employee_id.resource_calendar_id.two_weeks_calendar :
                    for day in rec.user_id.employee_id.resource_calendar_id.attendance_ids:
                        one_week_days.append(day.dayofweek)
                    weekdays.update({'one_week_days':one_week_days})
                else:
                    for day in rec.user_id.employee_id.resource_calendar_id.attendance_ids:
                        if not (day.name == 'Even week' or day.name =='Odd week'):
                            if day.week_type == '0':
                                even_week_days.append(day.dayofweek)
                            elif day.week_type == '1':
                                odd_week_days.append(day.dayofweek)
                            else:
                                continue
                    weekdays.update({
                        'even_week_days':even_week_days,
                        'odd_week_days':odd_week_days
                    })

                if (rec.planned_hours+store_hours) <= average_hrs:
                    rec.estimated_deadline = rec.start_date
                    rec.is_estimated_deadline = True
                else:
                    no_of_days = 0
                    tot_days_quot = float(int((rec.planned_hours+store_hours+non_working_days_hours) / average_hrs))
                    tot_days_rem = float(int((rec.planned_hours+store_hours+non_working_days_hours) % average_hrs))
                    if tot_days_rem == 0:
                        no_of_days = tot_days_quot -1
                        current_date = rec.start_date
                        week = current_date.isocalendar()[1] - current_date.replace(day=1).isocalendar()[1]
                        if 'one_week_days' in weekdays:
                            while no_of_days > 0:
                                current_date += timedelta(days=1)
                                weekday = current_date.weekday()
                                if str(weekday) not in one_week_days:
                                    continue
                                elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                    for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                            no_of_days += 1
                                no_of_days -= 1
                        elif 'even_week_days' and 'odd_week_days' in weekdays:
                            if week % 2 == 0:
                                while no_of_days > 0:
                                    current_date += timedelta(days=1)
                                    weekday = current_date.weekday()
                                    if str(weekday) not in even_week_days:
                                        continue
                                    elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                            if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                                no_of_days +=1
                                    no_of_days -= 1
                            else:
                                while no_of_days > 0:
                                    current_date += timedelta(days=1)
                                    weekday = current_date.weekday()
                                    if str(weekday) not in even_week_days:
                                        continue
                                    elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                            if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                                no_of_days +=1
                                    no_of_days -= 1
                        rec.estimated_deadline = current_date
                        # rec.estimated_deadline = rec.start_date + timedelta(days=no_of_days)
                        rec.is_estimated_deadline = True
                    else:
                        no_of_days = tot_days_quot
                        current_date = rec.start_date
                        week = current_date.isocalendar()[1] - current_date.replace(day=1).isocalendar()[1]
                        if 'one_week_days' in weekdays:
                            while no_of_days > 0:
                                current_date += timedelta(days=1)
                                weekday = current_date.weekday()
                                if str(weekday) not in one_week_days:
                                    continue
                                elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                    for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                            no_of_days += 1
                                no_of_days -= 1
                        elif 'even_week_days' and 'odd_week_days' in weekdays:
                            if week % 2 == 0:
                                while no_of_days > 0:
                                    current_date += timedelta(days=1)
                                    weekday = current_date.weekday()
                                    if str(weekday) not in even_week_days:
                                        continue
                                    elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                            if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                                no_of_days +=1
                                    no_of_days -= 1

                            else:
                                while no_of_days > 0:
                                    current_date += timedelta(days=1)
                                    weekday = current_date.weekday()
                                    if str(weekday) not in odd_week_days:
                                        continue
                                    elif rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                        for holiday in rec.user_id.employee_id.resource_calendar_id.global_leave_ids:
                                            if current_date >= holiday.date_from.date() and current_date <= holiday.date_to.date():
                                                no_of_days +=1

                                    no_of_days -= 1


                        # rec.estimated_deadline = rec.start_date + timedelta(days=no_of_days)
                        rec.estimated_deadline = current_date
                        rec.is_estimated_deadline = True

                        # if tot_days_quot <=0 and tot_days_rem > 0:
                        #     rec.estimated_deadline = rec.start_date + timedelta(days=tot_days_rem-1)
                        # elif tot_days_quot >0 and tot_days_rem >0:
                        #     rec.estimated_deadline = rec.start_date + timedelta(days=tot_days_quot)
                        # else:
                        #     rec.estimated_deadline = rec.start_date + timedelta(days=tot_days_quot -1)
            else:
                # rec.estimated_deadline = today
                rec.is_estimated_deadline = False
    @api.depends('sale_order_id')
    def update_so_description(self):
        for rec in self:
            if rec.sale_order_id:
                rec.so_description = rec.sale_order_id.so_desc
            else:
                rec.so_description = ""

    project_resource = fields.Many2one('hr.department', string="Resource")
    # estimated_deadline = fields.Date("Estimated Deadline",compute='calc_closure_date')
    estimated_deadline = fields.Date("Finish Date")
    so_description = fields.Text("SO Description",compute='update_so_description')
    is_a_template = fields.Boolean(related='project_id.is_a_template')
    is_estimated_deadline = fields.Boolean(compute=_onchange_estimate_deadline)

    # @api.onchange('project_id')
    # def _onchange_user_login(self):
    #     user = self.env.user
    #     if self.project_id and self.project_id.user_id.id == user.id:
    #         self.is_user=True
    #     else:
    #         self.is_user = False




    # def write(self, vals):
    #     if self.project_id.state != 'locked':
    #         task_id = self.env['project.task'].search([('project_id', '=', self.project_id.id)])
    #         for task in task_id:
    #             if task.stage_id == self.project_id.final_stage and task.kanban_state == 'done':
    #                 self.project_id.write({'state': 'locked'})
    #             else:
    #                 self.project_id.write({'state': 'draft'})
    #     return super(ProjectTaskInherit, self).write(vals)

    # @api.depends('timesheet_ids')
    # def calc_closure_date(self):
    #     dates = []
    #     tot_days = 0.0
    #     today = datetime.today()
    #     if self.timesheet_ids:
    #         for timesheet in self.timesheet_ids:
    #             dates.append(timesheet.date)
    #         max_date = max(dates)
    #         for timesheet in self.timesheet_ids:
    #             if max_date == timesheet.date:
    #                 tot_days += timesheet.no_of_days
    #         self.estimated_deadline = max_date + timedelta(days=tot_days)
    #     else:
    #         self.estimated_deadline = today


    #resource_details = fields.Many2one('project.task', string="Resource Details")

    # def action_view_tasks(self):
    #     res = super(Project, self).action_view_tasks()
    #     if self.project_template:
    #         self.type_ids = [(6, 0, self.project_template.type_ids.ids)]
    #     return res



class ProjectTasType(models.Model):
    _inherit = 'project.task.type'

    legend_new = fields.Char(
        'Blue Kanban Label', default=lambda s: _('New'), translate=True, required= True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_paused = fields.Char(
        'Yellow Kanban Label', default=lambda s: _('Paused'), translate=True, required= True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
