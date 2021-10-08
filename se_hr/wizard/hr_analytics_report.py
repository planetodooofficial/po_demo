from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import base64


class AnalyticsReport(models.TransientModel):
    _name = 'hr.analytics'

    data = fields.Binary("Output")
    file_name = fields.Char(string='File Name', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    filters = fields.Selection([('team',"Team wise"),('position',"Position Wise"),('recruiter',"Hiring  Manager wise"),('source',"Source")])
    teams = fields.Many2many('hr.department',string="Teams")
    source = fields.Many2many('utm.source',string="Sources")
    position = fields.Many2many('hr.job',string="Positions")
    recruiter = fields.Many2many('res.users',string="Hiring Managers")

    def print_hr_analytics(self):
        xls_filename = "HR Analytics Report.xlsx"
        workbook = xlsxwriter.Workbook(xls_filename)
        data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                  'font_size': 10, 'border': 1,'text_wrap': True})
        header_format = workbook.add_format({'valign': 'vcenter', 'font_size': 10, 'border': 1,'text_wrap': True})
        header_format.set_bold()
        header_format.set_align('center')

        #####Ageing of Job Positions##############
        if self.filters == 'position':
            jobs = self.env['hr.job'].search([])
        else:
            jobs = self.env['hr.job'].search([('id','in',self.position.ids)])

        if jobs:
            position_ageing_worksheet = workbook.add_worksheet("Ageing Of Open Positions")
            position_ageing_worksheet.set_column(0, 4, 25)
            position_ageing_worksheet.write(0, 0, 'Job Position', header_format)
            position_ageing_worksheet.write(0, 1, 'Opening Date', header_format)
            position_ageing_worksheet.write(0, 2, 'Closing Date', header_format)
            position_ageing_worksheet.write(0, 3, 'Position Ageing', header_format)
            position_ageing_worksheet.write(0, 4, 'Time taken to close', header_format)
            row=1

            for job in jobs:
                today = datetime.today()
                if job.opening_date:
                    age = str((job.opening_date - job.closing_date).days)+" Days" if job.closing_date and job.opening_date else False
                    time_to_close = str((today - job.opening_date).days)+" Days" if not age else ""
                    position_ageing_worksheet.write(row, 0,job.name, data_format)
                    position_ageing_worksheet.write(row, 1,job.opening_date.strftime('%d/%m/%Y') if job.opening_date else "-", data_format)
                    position_ageing_worksheet.write(row, 2,job.closing_date.strftime('%d/%m/%Y') if job.closing_date else "-", data_format)
                    position_ageing_worksheet.write(row, 3,age if age else "-",data_format)
                    # if time_to_close:
                    position_ageing_worksheet.write(row, 4,time_to_close if time_to_close else "-",data_format)


        ###############Time taken at each stage in every application##############
        domain = []
        if self.filters == 'team':
            domain.append(('department_id.id', 'in', self.teams.ids))
        if self.filters == 'position':
            domain.append(('job_id.id', 'in', self.position.ids))
        if self.filters == 'recruiter':
            domain.append(('user_id.id', 'in', self.recruiter.ids))
        if self.filters == 'source':
            domain.append(('source_id.id', 'in', self.source.ids))

        if domain:
            applications = self.env['hr.applicant'].search(domain)
        else:
            applications = self.env['hr.applicant'].search([])
        if applications:
            stage_time_worksheet = workbook.add_worksheet("Time Taken at stage")
            row=0
            for application in applications:
                last_col = len(application.stage_duration)
                stage_time_worksheet.merge_range(row,0,row,last_col-1,application.display_name,header_format)
                col = 0
                for stage in application.stage_duration:
                    diff = relativedelta(stage.date_stop,stage.date_start) if stage.date_start and stage.date_stop else ""
                    age = str(diff.minutes) + "Minutes" if stage.date_start and stage.date_stop else ""
                    stage_time_worksheet.write(row+1,col,stage.stage_id.name, header_format)
                    # stage_time_worksheet.write(row+2,col+1,stage.date_start.strftime('%d/%m/%Y') if stage.date_start else "", data_format)
                    # stage_time_worksheet.write(row+2,col+2,stage.date_stop.strftime('%d/%m/%Y') if stage.date_stop else "", data_format)
                    stage_time_worksheet.write(row+2,col,age, data_format)
                    col +=1
                stage_time_worksheet.set_column(0, col, 25)
                row +=4

        ########################### Cumulative Time taken at each stage ###############################

        cumulative_stage_time = workbook.add_worksheet("Cumulative time taken at stage")
        cumulative_stage_time.set_column(0, 1, 25)

        jobs = self.env['hr.job'].search([])
        row = 0
        for job in jobs:
            stages = self.env['hr.recruitment.stage'].search([])
            cumulative_stage_time.merge_range(row, 0, row, len(stages)- 1, job.display_name, header_format)
            col=0
            for stage in stages:
                stage_durations = self.env['recruitment.stage.duration'].search([('stage_id','=',stage.id),('application.job_id','=',job.id)])
                minutes = 0
                applications_list=[]
                for duration in stage_durations:
                    if duration.date_start and duration.date_stop:
                        if duration.application.id not in applications_list:
                            applications_list.append(duration.application.id)
                        diff = relativedelta(duration.date_stop,duration.date_start)
                        minutes += float(diff.minutes)
                    else:
                        minutes += 0
                average_minutes = minutes/len(applications_list) if len(applications_list) >0 and minutes >0 else 0
                cumulative_stage_time.write(row + 1, col, stage.name, data_format)
                cumulative_stage_time.write(row + 2, col, str(average_minutes) + " Minutes", data_format)
                col +=1
            row +=4

        ################# Time to close the position Per Application #################################

        close_time_per_app = workbook.add_worksheet("Closing time for position per recruitment")
        close_time_per_app.set_column(0, 1, 25)

        jobs = self.env['hr.job'].search([])
        row = 0
        for job in jobs:
            domain = []
            if self.filters == 'team':
                domain.append(('department_id.id', 'in', self.teams.ids))
            if self.filters == 'position':
                domain.append(('job_id.id', 'in', self.position.ids))
            if self.filters == 'recruiter':
                domain.append(('user_id.id', 'in', self.recruiter.ids))
            if self.filters == 'source':
                domain.append(('source_id.id', 'in', self.source.ids))
            if not self.filters == 'position':
                domain.append(('job_id','=',job.id))

            applications = self.env['hr.applicant'].search(domain)
            # col_range = (len(applications))*2
            if applications:
                # close_time_per_app.merge_range(row, 0, row, (len(applications)- 1)*2, job.display_name, header_format)
                close_time_per_app.merge_range(row, 0, row, ((len(applications))*2)-1, job.display_name, header_format)
                col=0
                for application in applications:
                    start_date = False
                    join_date = False
                    offer_date = False
                    join_minutes = 0
                    offer_minutes = 0
                    for stage in application.stage_duration:
                        if stage.stage_id.name == 'Sourcing':
                            start_date = stage.date_start
                        if stage.stage_id.name == 'Employee Creation':
                            join_date = stage.date_stop
                        if stage.stage_id.name == 'Offer checker':
                            offer_date = stage.date_stop
                    if start_date and join_date:
                        join_diff = relativedelta(join_date,start_date)
                        join_minutes += float(join_diff.minutes)
                    if start_date and offer_date:
                        offer_diff = relativedelta(offer_date,start_date)
                        offer_minutes += float(offer_diff.minutes)


                    close_time_per_app.merge_range(row+1, col, row+1, col+1, application.name, header_format)
                    close_time_per_app.write(row + 2, col,"Joining (Minutes)", data_format)
                    close_time_per_app.write(row + 2, col+1,"Offer Accept(Minutes)", data_format)
                    close_time_per_app.write(row + 3, col,str(join_minutes), data_format)
                    close_time_per_app.write(row + 3, col+1,str(offer_minutes), data_format)
                    col +=2
                row +=5


        ###########Interviews scheduled but did not happened##########################################

        domain = []
        if self.filters == 'team':
            domain.append(('department_id.id', 'in', self.teams.ids))
        if self.filters == 'position':
            domain.append(('job_id.id', 'in', self.position.ids))
        if self.filters == 'recruiter':
            domain.append(('user_id.id', 'in', self.recruiter.ids))
        if self.filters == 'source':
            domain.append(('source_id.id', 'in', self.source.ids))

        interviews_not_conducted = workbook.add_worksheet("Interviews Not Completed")
        interviews_not_conducted.set_column(0,1,25)

        if domain:
            applications = self.env['hr.applicant'].search(domain)
        else:
            applications = self.env['hr.applicant'].search([])

        if applications:
            interviews_not_conducted.write(0, 0, 'Interviews', header_format)
            row=1
            for application in applications:
                not_completed = False
                for duration in application.stage_duration:
                    if duration.stage_id.name == "HR Interview" and not duration.date_start:
                        not_completed = True
                if not_completed == True:
                    interviews_not_conducted.write(row, 0,application.display_name, data_format)
                    row +=1

        ####################How many interviews taken by an interviewer###############################################

        no_of_interviews_worksheet = workbook.add_worksheet("No. of Interviews")
        no_of_interviews_worksheet.set_column(0,1,25)
        users = self.env['res.users'].search([])
        no_of_interviews_worksheet.merge_range(1, 0, 2, 5, "NO. of Interviews taken by an Interviewer", header_format)

        no_of_interviews_worksheet.write(4, 0, 'Interviewer', header_format)
        no_of_interviews_worksheet.write(4, 1, 'No. of Interviews Taken', header_format)
        row = 5
        for user in users:
            domain = []
            if self.filters == 'team':
                domain.append(('department_id.id', 'in', self.teams.ids))
            if self.filters == 'position':
                domain.append(('job_id.id', 'in', self.position.ids))
            if self.filters == 'recruiter':
                domain.append(('user_id.id', 'in', self.recruiter.ids))
            if self.filters == 'source':
                domain.append(('source_id.id', 'in', self.source.ids))

            if domain:
                domain.append('|')
                domain.append(('interviewer1.id','=',user.id))
                domain.append(('interviewer2.id','=',user.id))
                interview = self.env['hr.applicant'].search(domain)
            else:
                interview = self.env['hr.applicant'].search(['|',('interviewer1.id','=',user.id),('interviewer2.id','=',user.id)])

            if len(interview) > 0:
                no_of_interviews_worksheet.write(row, 0, user.name, data_format)
                no_of_interviews_worksheet.write(row, 1, str(len(interview))+" Interviews", data_format)
                row +=1

        ################# Interview Rejection Reason and Source #########################

        domain = []
        if self.filters == 'team':
            domain.append(('department_id.id', 'in', self.teams.ids))
        if self.filters == 'position':
            domain.append(('job_id.id', 'in', self.position.ids))
        if self.filters == 'recruiter':
            domain.append(('user_id.id', 'in', self.recruiter.ids))
        if self.filters == 'source':
            domain.append(('source_id.id', 'in', self.source.ids))

        if domain:
            applications = self.env['hr.applicant'].search(domain)
        else:
            applications = self.env['hr.applicant'].search([])

        if applications:
            source_rejection_reason = workbook.add_worksheet("Interview Source and Rejection Reason")
            source_rejection_reason.set_column(0,4,25)
            source_rejection_reason.write(0, 0, 'Application', header_format)
            source_rejection_reason.write(0, 1, 'Source', header_format)

            source_rejection_reason.write(0, 3, 'Rejection Reason', header_format)
            source_rejection_reason.write(0, 4, 'Count', header_format)

            reasons = self.env['hr.applicant.refuse.reason'].search([])

            row = 1
            for application in applications:
                source_rejection_reason.write(row, 0, application.display_name, data_format)
                source_rejection_reason.write(row, 1, application.source_id.name, data_format)
                row +=1
            row = 1
            for reason1 in reasons:
                if domain:
                    domain.append(('refuse_reason_id.id','=',reason1.id))
                    refused_applications = self.env['hr.applicant'].search(domain)
                else:
                    refused_applications = self.env['hr.applicant'].search([('refuse_reason_id.id','=',reason1.id)])
                source_rejection_reason.write(row, 3, reason1.name, data_format)
                source_rejection_reason.write(row, 4, str(len(refused_applications))+" Applications", data_format)
                row +=1
        ########################Pipeline View############################################

        domain = []
        if self.filters == 'team':
            domain.append(('department_id.id', 'in', self.teams.ids))
        if self.filters == 'position':
            domain.append(('job_id.id', 'in', self.position.ids))
        if self.filters == 'recruiter':
            domain.append(('user_id.id', 'in', self.recruiter.ids))
        if self.filters == 'source':
            domain.append(('source_id.id', 'in', self.source.ids))

        if domain:
            domain.append(('is_rejected','=',False))
            applications = self.env['hr.applicant'].search(domain)
        else:
            applications = self.env['hr.applicant'].search([('is_rejected', '=', False)])

        if applications:
            pipeline_view = workbook.add_worksheet("View of Pipeline")
            pipeline_view.set_column(0,1,25)
            pipeline_view.write(0, 0, 'Application', header_format)
            pipeline_view.write(0, 1, 'In Stage', header_format)

            row = 1
            for application in applications:
                pipeline_view.write(row, 0, application.display_name, data_format)
                pipeline_view.write(row, 1, application.stage_id.name, data_format)
                row += 1


        workbook.close()
        self.write({
            'state': 'get',
            'data': base64.b64encode(open(xls_filename, 'rb').read()),
            'file_name': xls_filename
        })
        return {
            'name': 'HR Analytics Report',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
        # self.base_style = self.workbook.add_format({'text_wrap': True})
        # self.worksheet = self.workbook.add_worksheet()
