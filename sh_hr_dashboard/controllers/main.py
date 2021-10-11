# Copyright (C) Softhealer Technologies.

from odoo import http
from odoo.http import request
from datetime import timedelta
from datetime import datetime


class HRDashboard(http.Controller):

    @http.route('/get_employee_expense_data', type='http', auth="public", methods=['GET'])
    def get_employee_expense_data(self, **post):
        expenses = request.env['hr.expense'].sudo().search(
            [('employee_id.user_id', '=', request.env.user.id)], limit=10)
        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_expense_data_tbl', {'expenses': expenses})

    @http.route('/get_employee_attendance_data', type='http', auth="public", methods=['GET'])
    def get_employee_attendance_data(self, **post):
        attendances = request.env['hr.attendance'].sudo().search(
            [('employee_id.user_id', '=', request.env.user.id)], limit=10)
        attendance_dic = {}
        for attendance in attendances:
            data_list = []
            if attendance.check_in:
                data_list.append(attendance.check_in + timedelta(minutes=330))
            else:
                data_list.append('')

            if attendance.check_out:
                data_list.append(attendance.check_out + timedelta(minutes=330))
            else:
                data_list.append('')

            attendance_dic[attendance] = data_list
        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_attendance_data_tbl', {'attendance_dic': attendance_dic})

    @http.route('/get_employee_leave_data', type='http', auth="public", methods=['GET'])
    def get_employee_leave_data(self, **post):
        leaves = request.env['hr.leave'].sudo().search(
            [('employee_id.user_id', '=', request.env.user.id)], limit=10)
        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_leave_data_tbl', {'leaves': leaves})

    @http.route('/get_annoucement_data', type='http', auth="public", methods=['GET'])
    def get_annoucement_data(self, **post):
        annoucements = request.env['sh.annoucement'].sudo().search(
            [], order='sequence', limit=10)
        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_annoucements_data_tbl', {'annoucements': annoucements})

    @http.route('/get_employee_birhday_data', type='http', auth="public", methods=['GET'])
    def get_employee_birhday_data(self, **post):
        employees = request.env['hr.employee'].sudo().search([])
        employee_birthday_dic = {}
        today = datetime.today()
        todays_date = today.strftime("%m-%d")
        for employee in employees:
            if employee.birthday:
                birthdate = datetime.strptime(
                    employee.birthday.strftime("%m-%d"), "%m-%d")
                current_date = datetime.strptime(todays_date, "%m-%d")

                if(current_date >= birthdate):
                    days_diff = (current_date - birthdate).days

                    current_year = today.strftime("%Y")
                    if days_diff == 0:
                        employee_birthday_dic[employee] = days_diff
                    else:
                        if int(current_year) % 4 == 0:
                            days_diff = 366 - days_diff
                        else:
                            days_diff = 365 - days_diff
                else:
                    days_diff = (birthdate-current_date).days

                if days_diff >= 0:
                    employee_birthday_dic[employee] = days_diff

        sort_employee_birthday_dic = sorted(
            employee_birthday_dic.items(), key=lambda x: x[1])
        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_birthday_data_tbl', {'sort_employee_birthday_dic': sort_employee_birthday_dic})

    @http.route('/get_employee_anniversary_data', type='http', auth="public", methods=['GET'])
    def get_employee_anniversary_data(self, **post):
        employees = request.env['hr.employee'].sudo().search([])
        employee_anni_dic = {}
        today = datetime.today()
        todays_date = today.strftime("%m-%d")
        for employee in employees:
            if employee.date_of_joining:
                current_date = datetime.strptime(todays_date, "%m-%d")
                anni_date = datetime.strptime(
                    employee.date_of_joining.strftime("%m-%d"), "%m-%d")

                current_year = today.strftime("%Y")
                if(current_date >= anni_date):
                    days_diff = (current_date - anni_date).days

                    current_year = today.strftime("%Y")
                    if days_diff == 0:
                        employee_anni_dic[employee] = days_diff
                    else:
                        if int(current_year) % 4 == 0:
                            days_diff = 366 - days_diff
                        else:
                            days_diff = 365 - days_diff

                    employee_anni_dic[employee] = days_diff
                else:
                    days_diff = (anni_date-current_date).days

                    employee_anni_dic[employee] = days_diff

        sort_employee_anni_dic = sorted(
            employee_anni_dic.items(), key=lambda x: x[1])
        employee_anni_dic = {}
        for data in sort_employee_anni_dic:
            employee = data[0]
            anniversary_year = employee.date_of_joining.strftime("%Y")
            today = datetime.today()
            current_year = today.strftime("%Y")
            year_complete = int(current_year) - int(anniversary_year)
            employee_anni_dic[employee] = year_complete

        return request.env['ir.ui.view'].with_context()._render_template('sh_hr_dashboard.sh_anniversary_data_tbl', {'employee_anni_dic': employee_anni_dic, 'todays_date': todays_date})
