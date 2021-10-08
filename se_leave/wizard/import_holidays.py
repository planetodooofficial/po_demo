from odoo import api, fields, models, tools, SUPERUSER_ID,_
from io import StringIO
from tempfile import TemporaryFile
import base64
import csv
import datetime
from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser
from odoo.exceptions import UserError, ValidationError

class ImportHolidays(models.TransientModel):
    _name = 'holidays.import'

    upload_file = fields.Binary(string='LOAD FILE',required=True)
    location_name = fields.Char("Location:")
    type_of_calendar = fields.Selection([('two_week_working',"Two Week Working Calendar"),('one_week_working',"One Week Working Calendar")],"Import:",required=True)

    def import_holidays(self):
        csv_datas = self.upload_file
        fileobj = TemporaryFile('wb+')
        csv_datas = base64.decodestring(csv_datas)
        fileobj.write(csv_datas)
        fileobj.seek(0)
        str_csv_data = fileobj.read().decode('utf-8')
        lis = csv.reader(StringIO(str_csv_data), delimiter=',')
        working_row_num = 0
        holiday_row_num = 0
        holiday_importing = False

        weekly_days = {'Monday':'0','Tuesday':'1','Wednesday':'2','Thursday':'3','Friday':'4','Saturday':'5'
                       ,'Sunday':'6','Mon':'0','Tue':'1','Wed':'2','Thu':'3','Fri':'4','Sat':'5'
                       ,'Sun':'6'}
        working_calendar = []
        holiday_calendar = []
        even_idx = 0
        odd_idx = 0
        try:
            resource = self.env['resource.calendar'].create({
                'name': "Working hours of " + self.location_name,
                'tz': 'Asia/Calcutta',
                'company_id': self.env.company.id
            })
            for row in lis:
                if not holiday_row_num > 0:
                    if self.type_of_calendar == 'one_week_working':
                        if working_row_num==0:
                            resource.attendance_ids.unlink()
                            working_calendar.append((0, 0, {
                                'name': _(row[0]),
                                'dayofweek': weekly_days[row[1]],
                                'hour_from': float(row[2]),
                                'day_period': 'morning',
                                'hour_to': float(row[3]),
                            }))
                    elif self.type_of_calendar == 'two_week_working':
                        if working_row_num==0:
                            resource.attendance_ids.unlink()
                            resource.attendance_ids = [(0, 0, {
                                'name': 'Even week',
                                'dayofweek': '0',
                                'sequence': '0',
                                'hour_from': 0,
                                'day_period': 'morning',
                                'week_type': '0',
                                'hour_to': 0,
                                'display_type':
                                    'line_section'}),

                                (0, 0, {
                                    'name': 'Odd week',
                                    'dayofweek': '0',
                                    'sequence': '25',
                                    'hour_from': 0,
                                    'day_period':'morning',
                                    'week_type': '1',
                                    'hour_to': 0,
                                    'display_type': 'line_section'})]

                            resource.two_weeks_calendar = True
                        if working_row_num >0:
                            if resource:
                                if 'Even' == row[4].capitalize():
                                    working_calendar.append((0,0,{
                                            'name': _(row[0]),
                                            'dayofweek': weekly_days[row[1]],
                                            'sequence': even_idx+1,
                                            'hour_from': float(row[2]),
                                            'day_period': 'morning',
                                            'week_type': '0',
                                            'hour_to': float(row[3]),
                                            # 'display_type':'line_section'
                                        }))

                                    even_idx +=1
                                if 'Odd' == row[4].capitalize():
                                    working_calendar.append((0,0,{
                                            'name': _(row[0]),
                                            'dayofweek': weekly_days[row[1]],
                                            'sequence': odd_idx+26,
                                            'hour_from': float(row[2]),
                                            'day_period': 'morning',
                                            'week_type': '1',
                                            'hour_to': float(row[3]),
                                            # 'display_type':'line_section'
                                        }))

                                    odd_idx +=1

                    working_row_num += 1

                if "Holiday" in row[0].capitalize():
                    holiday_importing = True
                    resource.global_leave_ids.unlink()
                if holiday_importing:
                    if holiday_row_num > 2:
                        date_obj = dt.strptime(row[1],'%m/%d/%Y %H:%M:%S')
                        date2_obj = dt.strptime(row[2],'%m/%d/%Y %H:%M:%S')
                        # holiday_calendar.append((0,0,{
                        #     'name':row[0],
                        #     'date_from':dt.strptime(row[1],'%m/%d/%Y %H:%M:%S'),
                        #     'date_to':dt.strptime(row[2],'%m/%d/%Y %H:%M:%S')
                        # }))
                        holiday = self.env['resource.calendar.leaves'].create({
                            'name': row[0],
                            'date_from': dt.strptime(row[1], '%m/%d/%Y %H:%M:%S'),
                            'date_to': dt.strptime(row[2], '%m/%d/%Y %H:%M:%S'),
                            'calendar_id':resource.id
                        })
                        holiday_calendar.append(holiday.id)
                    holiday_row_num +=1

            if working_calendar:
                resource.attendance_ids = working_calendar
            if holiday_calendar:
                resource.global_leave_ids = [(6,0,holiday_calendar)]


        except Exception as e:
            raise ValidationError(e)