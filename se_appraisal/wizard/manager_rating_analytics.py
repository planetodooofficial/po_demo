from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import base64


class PmsRating(models.TransientModel):
    _name = 'pms.rating'

    data = fields.Binary("Output")
    file_name = fields.Char(string='File Name', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    filters = fields.Selection([('manager',"Managers"),('team_level',"Team Level")])
    manager_wise = fields.Many2many('hr.employee',string="Managers")
    team_wise = fields.Many2many('hr.department',string="Department")

    def print_pms_manager_rating_analytics(self):
        xls_filename = "PMS Rating Analytics Report.xlsx"
        workbook = xlsxwriter.Workbook(xls_filename)
        data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                  'font_size': 10, 'border': 1,'text_wrap': True})
        header_format = workbook.add_format({'valign': 'vcenter', 'font_size': 10, 'border': 1,'text_wrap': True})
        header_format.set_bold()
        header_format.set_align('center')

        ########################### Consistently high/low rating ############################################
        high_or_low_rating = workbook.add_worksheet("Employees with high/low rating")
        high_or_low_rating.set_column(0, 3, 25)

        employees = self.env['hr.employee'].search([])
        high_self_emps=[]
        low_self_emps = []

        high_manager_emps = []
        low_manager_emps = []
        for employee in employees:
            high_self_okrs = self.env['okr.master'].search([('employee_master','=',employee.id),('employee_overall_ratings','>=',4)])
            high_manager_okrs = self.env['okr.master'].search([('employee_master','=',employee.id),('manager_overall_ratings','>=',4)])

            if len(high_self_okrs) > 2:
                if not employee in high_self_emps:
                    high_self_emps.append(employee)

            if len(high_manager_okrs) > 2:
                if not employee in high_manager_emps:
                    high_manager_emps.append(employee)

            low_self_okrs = self.env['okr.master'].search([('employee_master','=',employee.id),('employee_overall_ratings','>=',2)])
            low_manager_okrs = self.env['okr.master'].search([('employee_master','=',employee.id),('manager_overall_ratings','>=',2)])

            if len(low_self_okrs) > 2:
                if not employee in low_self_emps:
                    low_self_emps.append(employee)

            if len(low_manager_okrs) > 2:
                if not employee in low_manager_emps:
                    low_manager_emps.append(employee)

        high_or_low_rating.merge_range(0, 0, 0, 1, 'Employee Rating', header_format)
        high_or_low_rating.merge_range(0, 2, 0, 3, 'Manager rating', header_format)

        high_or_low_rating.write(1,0, 'High Rating', header_format)
        high_or_low_rating.write(1,1, 'Low Rating', header_format)

        high_or_low_rating.write(1, 2, 'High Rating', header_format)
        high_or_low_rating.write(1, 3, 'Low Rating', header_format)

        high_self_row = 1
        low_self_row = 1

        high_manager_row = 1
        low_manager_row = 1

        for emp in high_self_emps:
            high_or_low_rating.write(high_self_row, 0, emp.name, data_format)
            high_self_row +=1

        for emp in low_self_emps:
            high_or_low_rating.write(low_self_row, 1, emp.name, data_format)
            low_self_row +=1

        for emp in high_manager_emps:
            high_or_low_rating.write(high_manager_row, 2, emp.name, data_format)
            high_manager_row +=1

        for emp in low_manager_emps:
            high_or_low_rating.write(low_manager_row, 3, emp.name, data_format)
            low_manager_row +=1

        #####managers##############
        if self.manager_wise:
            managers_rating_worksheet = workbook.add_worksheet("Managers Wise Rating")
            managers_rating_worksheet.set_column(0,2,25)
            managers_rating_worksheet.merge_range(0, 0, 2, 2, "Managers Wise Rating", header_format)

            row = 4
            for rec in self.manager_wise:
                manager_name = self.env['hr.employee'].search([('parent_id', '=', rec.id)])

                manager_count = self.env['hr.employee'].search_count([('parent_id', '=', rec.id)])
                managers_rating_worksheet.merge_range(row, 0,row+2 , 2, rec.name, header_format)

                row+=3
                managers_rating_worksheet.merge_range(row, 0, row+1, 0, 'Ratings', header_format)
                managers_rating_worksheet.merge_range(row, 1, row, 2, 'Percentages', header_format)
                managers_rating_worksheet.write(row+1, 1, 'Employee Overall Rating', header_format)
                managers_rating_worksheet.write(row+1, 2, 'Manager Overall Rating', header_format)

                row +=2

                for rating_count in range(1,6):
                    count_of_self_employees=0
                    count_of_manager_employees=0
                    self_percentages=0
                    manager_percentages=0
                    employees_okr = self.env['okr.master'].search([('employee_master', 'in', manager_name.ids)])
                    for counts in employees_okr:
                        if counts.manager_overall_ratings >=rating_count and counts.manager_overall_ratings < rating_count+1:
                            count_of_manager_employees +=1

                        if counts.employee_overall_ratings >= rating_count and counts.employee_overall_ratings < rating_count+1:
                            count_of_self_employees +=1

                    if manager_count !=0 and count_of_self_employees !=0:
                        self_percentages =(count_of_self_employees/manager_count) * 100

                    if manager_count !=0 and count_of_manager_employees !=0:
                        manager_percentages = (count_of_manager_employees/manager_count) * 100

                    managers_rating_worksheet.write(row, 0,str(rating_count) , data_format)
                    managers_rating_worksheet.write(row, 1, str(self_percentages) +"%", data_format)
                    managers_rating_worksheet.write(row, 2, str(manager_percentages) +"%", data_format)
                    row +=1
                row +=1
                ############Team Wise#################
        elif self.team_wise:
            team_rating_worksheet = workbook.add_worksheet("Team wise Rating")
            team_rating_worksheet.set_column(0, 2, 25)
            team_rating_worksheet.merge_range(0, 0, 2, 2, "Team Level Rating", header_format)
            row = 4
            for rec in self.team_wise:
                depart_wise_emp = self.env['hr.employee'].search([('department_id', '=', rec.id)])
                depart_wise_emp_count = self.env['hr.employee'].search_count([('department_id', '=', rec.id)])
                team_rating_worksheet.merge_range(row, 0, row + 2, 2, rec.name, header_format)
                row += 3

                team_rating_worksheet.merge_range(row, 0, row + 1, 0, 'Ratings', header_format)
                team_rating_worksheet.merge_range(row, 1, row, 2, 'Percentages', header_format)
                team_rating_worksheet.write(row + 1, 1, 'Employee Overall Rating', header_format)
                team_rating_worksheet.write(row + 1, 2, 'Manager Overall Rating', header_format)

                row += 2
                for rating_count in range(1, 6):
                    count_of_dept_self_employee=0
                    count_of_dept_manager_employee=0
                    self_percentages = 0
                    manager_percentages = 0
                    employees_dept_okr = self.env['okr.master'].search([('employee_master', 'in', depart_wise_emp.ids)])

                    for counts in employees_dept_okr:
                        if counts.employee_overall_ratings >= rating_count and counts.employee_overall_ratings < rating_count+1:
                            count_of_dept_self_employee += 1

                    for counts in employees_dept_okr:
                        if counts.manager_overall_ratings >= rating_count and counts.manager_overall_ratings < rating_count+1:
                            count_of_dept_manager_employee += 1

                    if depart_wise_emp_count != 0 and count_of_dept_self_employee !=0:
                        self_percentages = (count_of_dept_self_employee / depart_wise_emp_count) * 100

                    if depart_wise_emp_count != 0 and count_of_dept_manager_employee !=0:
                        manager_percentages = (count_of_dept_manager_employee / depart_wise_emp_count) * 100

                    team_rating_worksheet.write(row, 0, str(rating_count), data_format)
                    team_rating_worksheet.write(row, 1, str(self_percentages) +"%", data_format)
                    team_rating_worksheet.write(row, 2, str(manager_percentages) +"%", data_format)
                    row += 1
                row += 1
        else:
            ################### Organisation level ################################################
            org_rating_worksheet = workbook.add_worksheet("Organisation level Rating")
            org_rating_worksheet.set_column(0, 2, 25)
            org_rating_worksheet.merge_range(0, 0, 2, 2, "Organisation Level Rating", header_format)
            row = 4
            emp = self.env['hr.employee'].search([])
            emp_count = self.env['hr.employee'].search_count([])
            org_rating_worksheet.merge_range(row, 0, row + 1, 0, 'Ratings', header_format)
            org_rating_worksheet.merge_range(row, 1, row, 2, 'Percentages', header_format)
            org_rating_worksheet.write(row + 1, 1, 'Employee Overall Rating', header_format)
            org_rating_worksheet.write(row + 1, 2, 'Manager Overall Rating', header_format)
            row += 2

            for rating_count in range(1, 6):
                count_of_self_employee = 0
                count_of_maanager_employee = 0
                self_percentages = 0
                manager_percentages = 0

                employees_dept_okr = self.env['okr.master'].search([('employee_master', 'in', emp.ids)])
                for counts in employees_dept_okr:
                    if counts.employee_overall_ratings >= rating_count and counts.employee_overall_ratings < rating_count+1:
                        count_of_self_employee += 1

                    if counts.manager_overall_ratings >= rating_count and counts.manager_overall_ratings < rating_count+1:
                        count_of_maanager_employee += 1

                if emp_count != 0 and count_of_self_employee != 0:
                    self_percentages = (count_of_self_employee / emp_count) * 100

                if emp_count != 0 and count_of_maanager_employee != 0:
                    manager_percentages = (count_of_maanager_employee / emp_count) * 100

                org_rating_worksheet.write(row, 0, str(rating_count), data_format)
                org_rating_worksheet.write(row, 1, str(self_percentages) + "%", data_format)
                org_rating_worksheet.write(row, 2, str(manager_percentages) + "%", data_format)
                row += 1
            row += 1
        workbook.close()
        self.write({
            'state': 'get',
            'data': base64.b64encode(open(xls_filename, 'rb').read()),
            'file_name': xls_filename
        })
        return {
            'name': 'PMS Rating Analytics Report',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }