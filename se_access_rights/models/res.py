from odoo import api, fields, models, _,tools


class Users(models.Model):
    _inherit = "res.users"

    # is_name = fields.Boolean('Is Name',compute="_compute_general_end_user_policy")

    # @api.onchange('groups_id')
    # def _onchange_general_end_user_policy(self):
    #     print('self',self)
    #     if self.has_group('se_custom.general_end_user_group').id:
    #         self.is_name = True
    #         self.groups_id = (4,[self.env.ref('project.group_project_user').id])
    #     else:
    #         self.is_name = False

    # @api.constrains('groups_id')
    # def _check_one_user_type(self):
    #     super(Users, self)._check_one_user_type()
    #
    #     g1 = self.env.ref('se_custom.general_end_user_group', False)
    #     seller_group_obj = self.env.ref('project.group_project_user')
    #     if g1:
    #         seller_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
    #     else:
    #         seller_group_obj.sudo().write({"users": [(3, self.id, 0)]})

    @api.model
    def create(self, vals):
        res = super(Users, self).create(vals)
        # general end user
        project_group_obj = self.env.ref('project.group_project_user')
        if res.has_group("se_access_rights.general_end_user_group"):
            project_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            project_group_obj.sudo().update({"users": [(3, res.id)]})
        timesheet_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_user')
        if res.has_group("se_access_rights.general_end_user_group"):
            timesheet_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            timesheet_group_obj.sudo().write({"users": [(3, res.id)]})
        # project superuser
        project_superuser_group_obj = self.env.ref('se_access_rights.group_template_admin')
        if res.has_group("se_access_rights.project_super_user_group"):
            project_superuser_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            project_superuser_group_obj.sudo().write({"users": [(3, res.id)]})

        # project manager
        timesheet_pm_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_approver')
        if res.has_group("se_access_rights.project_manager_user_group"):
            timesheet_pm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            timesheet_pm_group_obj.sudo().write({"users": [(3, res.id)]})
        expense_group_obj = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if res.has_group("se_access_rights.project_manager_user_group"):
            expense_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            expense_group_obj.sudo().write({"users": [(3, res.id)]})
        sales_group_obj = self.env.ref('sales_team.group_sale_salesman')
        purchase_request_po_group = self.env.ref('se_access_rights.group_request_for_po')
        if res.has_group("se_access_rights.project_manager_user_group"):
            purchase_request_po_group.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            purchase_request_po_group.sudo().write({"users": [(3, res.id)]})
        project_manager_group_obj = self.env.ref('project.group_project_manager')
        if res.has_group("se_access_rights.project_manager_user_group"):
            project_manager_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            project_manager_group_obj.sudo().write({"users": [(3, res.id)]})
        # BD USER
        if res.has_group("se_access_rights.bd_user_group"):
            sales_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            sales_group_obj.sudo().write({"users": [(3, res.id)]})
        # BD Manager
        bdm_sales_group_obj = self.env.ref('sales_team.group_sale_manager')
        if res.has_group("se_access_rights.bd_manager_user_group"):
            bdm_sales_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            bdm_sales_group_obj.sudo().write({"users": [(3, res.id)]})

        # Account user
        purchase_po_generation_group = self.env.ref('se_access_rights.group_po_generation')
        if res.has_group("se_access_rights.account_user_group"):
            purchase_po_generation_group.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            purchase_po_generation_group.sudo().write({"users": [(3, res.id)]})

        # Account Manager
        expense_group_obj = self.env.ref('hr_expense.group_hr_expense_manager')
        if res.has_group("se_access_rights.account_manager_group"):
            expense_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            expense_group_obj.sudo().write({"users": [(3, res.id)]})
        account_group_obj = self.env.ref('account.group_account_manager')
        if res.has_group("se_access_rights.account_manager_group"):
            account_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            account_group_obj.sudo().write({"users": [(3, res.id)]})
        purchase_po_approval_group = self.env.ref('se_access_rights.group_po_approval')
        if res.has_group("se_access_rights.account_manager_group"):
            purchase_po_approval_group.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            purchase_po_approval_group.sudo().write({"users": [(3, res.id)]})
        purchase_group_obj = self.env.ref('purchase.group_purchase_manager')
        if res.has_group("se_access_rights.account_manager_group"):
            purchase_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            purchase_group_obj.sudo().write({"users": [(3, res.id)]})

        # Reporting Manager
        timesheet_rm_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_approver')
        if res.has_group("se_access_rights.reporting_manager_group"):
            timesheet_rm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            timesheet_rm_group_obj.sudo().write({"users": [(3, res.id)]})
        expense_rm_group_obj = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if res.has_group("se_access_rights.reporting_manager_group"):
            expense_rm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            expense_rm_group_obj.sudo().write({"users": [(3, res.id)]})
        timeoff_rm_group_obj = self.env.ref('hr_holidays.group_hr_holidays_responsible')
        if res.has_group("se_access_rights.reporting_manager_group"):
            timeoff_rm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            timeoff_rm_group_obj.sudo().write({"users": [(3, res.id)]})
        # HR User
        employee_group_obj = self.env.ref('hr.group_hr_user')
        if res.has_group("se_access_rights.hr_user_group"):
            employee_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            employee_group_obj.sudo().write({"users": [(3, res.id)]})
        recruitment_group_obj = self.env.ref('hr_recruitment.group_hr_recruitment_user')
        if res.has_group("se_access_rights.hr_user_group"):
            recruitment_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            recruitment_group_obj.sudo().write({"users": [(3, res.id)]})
        contract_group_obj = self.env.ref('hr_contract.group_hr_contract_manager')
        if res.has_group("se_access_rights.hr_user_group"):
            contract_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            contract_group_obj.sudo().write({"users": [(3, res.id)]})
        attendence_group_obj = self.env.ref('hr_attendance.group_hr_attendance')
        if res.has_group("se_access_rights.hr_user_group"):
            attendence_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            attendence_group_obj.sudo().write({"users": [(3, res.id)]})
        # HR Manager
        recruitment_hm_group_obj = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
        if res.has_group("se_access_rights.hr_manager_group"):
            recruitment_hm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            recruitment_hm_group_obj.sudo().write({"users": [(3, res.id)]})
        contract_hm_group_obj = self.env.ref('hr_contract.group_hr_contract_manager')
        if res.has_group("se_access_rights.hr_manager_group"):
            contract_hm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            contract_hm_group_obj.sudo().write({"users": [(3, res.id)]})
        attendence_hm_group_obj = self.env.ref('hr_attendance.group_hr_attendance_manager')
        if res.has_group("se_access_rights.hr_manager_group"):
            attendence_hm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            attendence_hm_group_obj.sudo().write({"users": [(3, res.id)]})
        # Vendor

        # Vendor Manager
        purchase_vm_group_obj = self.env.ref('purchase.group_purchase_manager')
        if res.has_group("se_access_rights.vendor_manager_group"):
            purchase_vm_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            purchase_vm_group_obj.sudo().write({"users": [(3, res.id)]})
        # IT Manager
        maintenance_group_obj = self.env.ref('maintenance.group_equipment_manager')
        if res.has_group("se_access_rights.it_manager_group"):
            maintenance_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            maintenance_group_obj.sudo().write({"users": [(3, res.id)]})
        admin_group_obj = self.env.ref('base.group_system')
        if res.has_group("se_access_rights.it_manager_group"):
            admin_group_obj.sudo().write({'users': [(4, user.id) for user in res]})
        else:
            admin_group_obj.sudo().write({"users": [(3, res.id)]})

        ##For Admin Accesses
        admin_user = self.env.ref('base.group_system')
        if self.has_group("base.group_system"):
            admin_user.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            admin_user.sudo().write({"users": [(3, self.id)]})

        erp_manager = self.env.ref('base.group_erp_manager')
        if self.has_group("base.erp_manager"):
            erp_manager.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            erp_manager.sudo().write({"users": [(3, self.id)]})

        return res

    def write(self, values):
        res = super(Users, self).write(values)
        # if self.general_end_user_group or self.project_super_user_group or self.project_manager_user_group or self.bd_user_group or self.bd_manager_user_group or self.account_user_group or self.account_manager_group or self.reporting_manager_group or self.hr_user_group or self.hr_manager_group or self.vendor_manager_group or self.vendors_group or self.it_manager_group:
            #general end user group
        project_group_obj = self.env.ref('project.group_project_user')
        if self.has_group("se_access_rights.general_end_user_group"):
            project_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            project_group_obj.sudo().write({"users": [(3, self.id)]})
        #     timesheet groups
        timesheet_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_user')
        if self.has_group("se_access_rights.general_end_user_group"):
            timesheet_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            timesheet_group_obj.sudo().write({"users": [(3, self.id)]})
        #  project superuser
        project_superuser_group_obj = self.env.ref('se_access_rights.group_template_admin')
        if self.has_group("se_access_rights.project_super_user_group"):
            project_superuser_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            project_superuser_group_obj.sudo().write({"users": [(3, self.id)]})
            ##project manager group
        timesheet_pm_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_approver')
        if self.has_group("se_access_rights.project_manager_user_group"):
            timesheet_pm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            timesheet_pm_group_obj.sudo().write({"users": [(3, self.id)]})
        expense_group_obj = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if self.has_group("se_access_rights.project_manager_user_group"):
            expense_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            expense_group_obj.sudo().write({"users": [(3, self.id)]})
        purchase_request_po_group = self.env.ref('se_access_rights.group_request_for_po')
        if self.has_group("se_access_rights.project_manager_user_group"):
            purchase_request_po_group.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            purchase_request_po_group.sudo().write({"users": [(3, self.id)]})
        project_manager_group_obj = self.env.ref('project.group_project_manager')
        if self.has_group("se_access_rights.project_manager_user_group"):
            project_manager_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            project_manager_group_obj.sudo().write({"users": [(3, self.id)]})
        # BD USER
        sales_group_obj = self.env.ref('sales_team.group_sale_salesman')
        if self.has_group("se_access_rights.bd_user_group"):
            sales_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            sales_group_obj.sudo().write({"users": [(3, self.id)]})
        # BD Manager
        bdm_sales_group_obj = self.env.ref('sales_team.group_sale_manager')
        if self.has_group("se_access_rights.bd_manager_user_group"):
            bdm_sales_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            bdm_sales_group_obj.sudo().write({"users": [(3, self.id)]})
        # Account user
        purchase_po_generation_group = self.env.ref('se_access_rights.group_po_generation')
        if self.has_group("se_access_rights.account_user_group"):
            purchase_po_generation_group.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            purchase_po_generation_group.sudo().write({"users": [(3, self.id)]})
        # Account Manager
        expense_group_obj = self.env.ref('hr_expense.group_hr_expense_manager')
        if self.has_group("se_access_rights.account_manager_group"):
            expense_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            expense_group_obj.sudo().write({"users": [(3, self.id)]})
        account_group_obj = self.env.ref('account.group_account_manager')
        if self.has_group("se_access_rights.account_manager_group"):
            account_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            account_group_obj.sudo().write({"users": [(3, self.id)]})
        purchase_po_approval_group = self.env.ref('se_access_rights.group_po_approval')
        if self.has_group("se_access_rights.account_manager_group"):
            purchase_po_approval_group.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            purchase_po_approval_group.sudo().write({"users": [(3, self.id)]})
        # Reporting Manager
        timesheet_rm_group_obj = self.env.ref('hr_timesheet.group_hr_timesheet_approver')
        if self.has_group("se_access_rights.reporting_manager_group"):
            timesheet_rm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            timesheet_rm_group_obj.sudo().write({"users": [(3, self.id)]})
        expense_rm_group_obj = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if self.has_group("se_access_rights.reporting_manager_group"):
            expense_rm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            expense_rm_group_obj.sudo().write({"users": [(3, self.id)]})
        timeoff_rm_group_obj = self.env.ref('hr_holidays.group_hr_holidays_responsible')
        if self.has_group("se_access_rights.reporting_manager_group"):
            timeoff_rm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            timeoff_rm_group_obj.sudo().write({"users": [(3, self.id)]})
        # HR User
        employee_group_obj = self.env.ref('hr.group_hr_user')
        if self.has_group("se_access_rights.hr_user_group"):
            employee_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            employee_group_obj.sudo().write({"users": [(3, self.id)]})
        recruitment_group_obj = self.env.ref('hr_recruitment.group_hr_recruitment_user')
        if self.has_group("se_access_rights.hr_user_group"):
            recruitment_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            recruitment_group_obj.sudo().write({"users": [(3, self.id)]})
        contract_group_obj = self.env.ref('hr_contract.group_hr_contract_manager')
        if self.has_group("se_access_rights.hr_user_group"):
            contract_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            contract_group_obj.sudo().write({"users": [(3, self.id)]})
        attendence_group_obj = self.env.ref('hr_attendance.group_hr_attendance')
        if self.has_group("se_access_rights.hr_user_group"):
            attendence_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            attendence_group_obj.sudo().write({"users": [(3, self.id)]})
        # HR Manager
        recruitment_hm_group_obj = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
        if self.has_group("se_access_rights.hr_manager_group"):
            recruitment_hm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            recruitment_hm_group_obj.sudo().write({"users": [(3, self.id)]})
        contract_hm_group_obj = self.env.ref('hr_contract.group_hr_contract_manager')
        if self.has_group("se_access_rights.hr_manager_group"):
            contract_hm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            contract_hm_group_obj.sudo().write({"users": [(3, self.id)]})
        attendence_hm_group_obj = self.env.ref('hr_attendance.group_hr_attendance_manager')
        if self.has_group("se_access_rights.hr_manager_group"):
            attendence_hm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            attendence_hm_group_obj.sudo().write({"users": [(3, self.id)]})
        payroll_hm_group_obj = self.env.ref('hr_payroll_community.group_hr_payroll_community_manager')
        if self.has_group("se_access_rights.hr_manager_group"):
            payroll_hm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            payroll_hm_group_obj.sudo().write({"users": [(3, self.id)]})

        # Vendor

        # Vendor Manager
        purchase_vm_group_obj = self.env.ref('purchase.group_purchase_manager')
        if self.has_group("se_access_rights.vendor_manager_group"):
            purchase_vm_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            purchase_vm_group_obj.sudo().write({"users": [(3, self.id)]})
        # IT Manager
        maintenance_group_obj = self.env.ref('maintenance.group_equipment_manager')
        if self.has_group("se_access_rights.it_manager_group"):
            maintenance_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            maintenance_group_obj.sudo().write({"users": [(3, self.id)]})
        admin_group_obj = self.env.ref('base.group_system')
        if self.has_group("se_access_rights.it_manager_group"):
            admin_group_obj.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            admin_group_obj.sudo().write({"users": [(3, self.id)]})


        ##For Admin Accesses
        admin_user = self.env.ref('base.group_system')
        erp_manager = self.env.ref('base.group_erp_manager')
        if self.has_group("base.group_erp_manager"):
            erp_manager.sudo().write({'users': [(4, user.id) for user in self]})
        else:
            if self.has_group("base.group_system"):
                admin_user.sudo().write({'users': [(4, user.id) for user in self]})

        return res

