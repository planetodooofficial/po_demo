from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool, xlsxwriter, file_open
import calendar
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import base64


class AnalyticsReport(models.TransientModel):
    _name = 'leave.report'

    data = fields.Binary("Output")
    file_name = fields.Char(string='File Name', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report_type = fields.Selection([('cur_leave_bal',"Current Leave Balance"),('day_wise_chk_inout',"Day Wise Check In/Out"),('leaves_taken',"Leaves Taken Monthly"),('current_leave_req',"Current Leave Requests"),('reliev_emp_leave_balance',"Relieved Employee Leave Balance")],
                                   string="Report for:",required=True)
    date_from = fields.Date("From")
    date_to = fields.Date("To")

    def print_leave_reports(self):
        xls_filename = "Leave Report.xlsx"
        workbook = xlsxwriter.Workbook(xls_filename)
        data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                  'font_size': 10, 'border': 1,'text_wrap': True})
        header_format = workbook.add_format({'valign': 'vcenter', 'font_size': 10, 'border': 1,'text_wrap': True})
        header_format.set_bold()
        header_format.set_align('center')

        ######### Month End leave requests ##############
        if self.report_type == 'current_leave_req':
            monthly_leave_req = workbook.add_worksheet("Current leave requests")
            monthly_leave_req.set_column(0, 4, 25)
            emaployees = self.env['hr.employee'].search([])
            row = 0
            for emp in emaployees:
                domain = [('state', 'not in', ('cancel', 'refuse', 'validate')), ('employee_id', '=', emp.id)]
                if self.date_from and self.date_to:
                    domain.append(('request_date_from','>=',self.date_from))
                    domain.append(('request_date_to','<=',self.date_to))
                leaves = self.env['hr.leave'].search(domain)
                if leaves:
                    monthly_leave_req.merge_range(row, 0, row, 3, emp.name, header_format)
                    row +=1
                    monthly_leave_req.write(row,0,"Date From", header_format)
                    monthly_leave_req.write(row,1,"Date To", header_format)
                    monthly_leave_req.write(row,2,"No. Of Days", header_format)
                    monthly_leave_req.write(row,3,"Status", header_format)
                    row +=1
                    for leave in leaves:
                        if leave.state == 'draft':
                            status="To Submit"
                        elif leave.state == 'cancel':
                            status = "Cancelled"
                        elif leave.state == 'refuse':
                            status = "Refused"
                        elif leave.state == 'confirm':
                            status = "To Approve"
                        elif leave.state == 'validate1':
                            status = "Second Approval"
                        else:
                            status = "Approved"

                        monthly_leave_req.write(row, 0,date.strftime(leave.request_date_from,"%d/%m/%Y"), data_format)
                        monthly_leave_req.write(row, 1,date.strftime(leave.request_date_to,"%d/%m/%Y"), data_format)
                        monthly_leave_req.write(row, 2,leave.number_of_days, data_format)
                        monthly_leave_req.write(row, 3,status, data_format)
                        row +=1
                    row +=2

        ######### Leaves taken in date range##############

        if self.report_type == 'leaves_taken':
            employees = self.env['hr.employee'].search([])
            leaves_taken = workbook.add_worksheet("Monthly Leaves Taken")
            leaves_taken.set_column(0, 4, 25)
            row = 0
            for emp in employees:
                domain = [('employee_id', '=', emp.id)]
                if self.date_from and self.date_to:
                    domain.append(('create_date', '>=', self.date_from))
                    domain.append(('create_date', '<=', self.date_to))

                leaves = self.env['hr.leave'].search(domain)
                if leaves:
                    leaves_taken.merge_range(row, 0, row, 3, emp.name, header_format)
                    row +=1
                    leaves_taken.write(row, 0, "Date From", header_format)
                    leaves_taken.write(row, 1, "Date To", header_format)
                    leaves_taken.write(row, 2, "No. Of Days", header_format)
                    leaves_taken.write(row, 3, "Status", header_format)
                    row +=1
                    tot_leaves = 0.0
                    for leave in leaves:
                        if leave.state == 'draft':
                            status = "To Submit"
                        elif leave.state == 'cancel':
                            status = "Cancelled"
                        elif leave.state == 'refuse':
                            status = "Refused"
                        elif leave.state == 'confirm':
                            status = "To Approve"
                        elif leave.state == 'validate1':
                            status = "Second Approval"
                        else:
                            status = "Approved"

                        tot_leaves += leave.number_of_days

                        leaves_taken.write(row, 0, date.strftime(leave.request_date_from, "%d/%m/%Y"),
                                                data_format)
                        leaves_taken.write(row, 1, date.strftime(leave.request_date_to, "%d/%m/%Y"),
                                                data_format)
                        leaves_taken.write(row, 2, leave.number_of_days, data_format)
                        leaves_taken.write(row, 3, status, data_format)
                        row +=1
                    leaves_taken.merge_range(row, 0, row, 1,"Total Leaves", header_format)
                    leaves_taken.write(row, 2,tot_leaves, data_format)
                    leaves_taken.write(row, 3,"", data_format)
                    row += 2
        ######### Current Leave Balance##################

        if self.report_type == 'curr_leave_bal':

            employees = self.env['hr.employee'].search([])
            leave_types = self.env['hr.leave.type'].search([])
            if employees:
                row= 0
                leave_balance = workbook.add_worksheet("Current Leave Balance")
                leave_balance.set_column(0, 4, 25)
                for employee in employees:
                    leave_balance.merge_range(row, 0, row, (len(leave_types)) - 1,employee.name, header_format)
                    col = 0
                    for leave_rec in employee.leaves:
                        leave_balance.write(row+1, col,leave_rec.leave_type.name, header_format)
                        leave_balance.write(row+2, col,str(leave_rec.leaves_balance), data_format)
                        col +=1
                    row +=5

        if self.report_type == 'reliev_emp_leave_balance':

            resigned = self.env['hr.resignation'].search([('state','=','confirm')])
            leave_types = self.env['hr.leave.type'].search([])
            if resigned:
                row= 0
                relieved_leave_balance = workbook.add_worksheet("Relieved Employee Leave Balance")
                relieved_leave_balance.set_column(0, 4, 25)
                for employee in resigned:
                    relieved_leave_balance.merge_range(row, 0, row, (len(leave_types)) - 1,employee.employee_id.name, header_format)
                    col = 0
                    for leave_rec in employee.employee_id.leaves:
                        relieved_leave_balance.write(row+1, col,leave_rec.leave_type.name, header_format)
                        relieved_leave_balance.write(row+2, col,str(leave_rec.leaves_balance), data_format)
                        col +=1
                    row +=5
        ######### Monthly Day wise check in/out time##################

        if self.report_type == 'day_wise_chk_inout':
            employees = self.env['hr.employee'].search([])
            monthly_daily_check_in_out = workbook.add_worksheet("Monthly day wise check in/out")
            monthly_daily_check_in_out.set_column(0, 4, 25)
            row = 0
            for employee in employees:
                monthly_daily_check_in_out.merge_range(row, 0, row, 2, employee.name, header_format)
                attendances = self.env['hr.attendance'].search([('employee_id','=',employee.id)], order='create_date ASC')
                col =0
                for i in range(len(attendances)):
                    monthly_daily_check_in_out.write(row + 1, col,"Month", header_format)
                    monthly_daily_check_in_out.write(row + 1, col+1,"Check In", header_format)
                    monthly_daily_check_in_out.write(row + 1, col+2,"Check Out", header_format)

                    attendance = attendances[i]
                    if i == 0:
                        monthly_daily_check_in_out.write(row+1, col,calendar.month_name[attendances[i].create_date.month], data_format)
                        monthly_daily_check_in_out.write(row + 1, col + 1,datetime.strftime(attendance.check_in, "%d/%m/%Y %H:%M:%S"),data_format)
                        monthly_daily_check_in_out.write(row + 1, col + 2,datetime.strftime(attendance.check_out, "%d/%m/%Y %H:%M:%S"),data_format)
                    else:
                        if calendar.month_name[attendances[i].create_date.month] == calendar.month_name[attendances[i-1].create_date.month]:
                            monthly_daily_check_in_out.write(row+1, col,"", data_format)
                            monthly_daily_check_in_out.write(row+1, col+1,datetime.strftime(attendance.check_in,"%d/%m/%Y %H:%M:%S"), data_format)
                            monthly_daily_check_in_out.write(row+1, col+2,datetime.strftime(attendance.check_out,"%d/%m/%Y %H:%M:%S"), data_format)

                        if calendar.month_name[attendances[i].create_date.month] != calendar.month_name[attendances[i-1].create_date.month]:
                            monthly_daily_check_in_out.write(row + 1, col, calendar.month_name[attendances[i].create_date.month], data_format)
                            monthly_daily_check_in_out.write(row + 1, col + 1,datetime.strftime(attendance.check_in, "%d/%m/%Y %H:%M:%S"),data_format)
                            monthly_daily_check_in_out.write(row + 1, col + 2,datetime.strftime(attendance.check_out, "%d/%m/%Y %H:%M:%S"),data_format)
                    row +=2
                row +=2

        workbook.close()
        self.write({
            'state': 'get',
            'data': base64.b64encode(open(xls_filename, 'rb').read()),
            'file_name': xls_filename
        })
        return {
            'name': 'Leave Reports',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # self.base_style = self.workbook.add_format({'text_wrap': True})
        # self.worksheet = self.workbook.add_worksheet()
