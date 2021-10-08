from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
import logging
from datetime import datetime, date
import requests
import json


logger = logging.getLogger(__name__)


class ApproveReject(http.Controller):

    @http.route('/approve/<string:id>', type='http', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def approval_details(self, id, **post):
        cand_offer = request.env['offer.letter'].sudo().search([('id', '=', int(id))])
        hr_record = request.env['hr.applicant'].sudo().search([('id', '=', cand_offer.cand_name.id)], limit=1)
        print(hr_record)
        for rec in hr_record:
            if rec.name and rec.email_from:
                mail_values = {}
                mail_values.update({
                    'body_html': """
                                      <p>Dear """ + rec.partner_name + """</p>
                                      <p>Thanks for confirmation.</p>
                                      <br/>
    
                                                                  """
                })
                mail_values.update({
                    'subject': rec.name + '  Confirmation Mail',
                    'email_to': rec.email_from,
                })
                msg_id_managaer = request.env['mail.mail'].sudo().create(mail_values)
                msg_id_managaer.send()
                stage = request.env['hr.recruitment.stage'].search([('name','=',"Offer Accepted")],limit=1)
                rec.stage_id = stage.id
            else:
                print(hr_record)
        if not cand_offer.is_approve_cand:
            cand_offer.is_approve_cand = True
        else:
            cand_offer.is_approve_cand = False
        return request.render("website_form.contactus_thanks")



    @http.route('/approve_hod/<string:id>', type='http', auth="user", methods=['GET', 'POST'], website=True,
                csrf=False)
    def approval_hr_details(self, id, **post):
        print(id)
        hr_record = request.env['offer.letter'].sudo().search([('id', '=', int(id))], limit=1)
        for hr in hr_record:
            hr.sudo().update({'state': 'approved'})
            hr.cand_name.is_approve = True
        print(hr_record)
        users = hr_record.env['res.users'].search([])
        for auth_user in users:
            if auth_user.has_group('se_hr.group_HR_hod_user'):
                mail_values = {}
                mail_values.update({
                    'body_html': """
                                      <p>Dear """ + auth_user.name + """</p>
                                      <p>Thanks for confirmation.</p>
                                      <br/>
    
                                                                  """
                })
                mail_values.update({
                    'subject': auth_user.name+ 'Confirmation Mail',
                    'email_to':auth_user.login,
                })
                msg_id_managaer = request.env['mail.mail'].sudo().create(mail_values)
                msg_id_managaer.send()










