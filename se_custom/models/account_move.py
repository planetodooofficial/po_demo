from odoo import api, fields, models, _
from datetime import datetime, time


class AccountMove(models.Model):
    _inherit = 'account.move'

    name = fields.Char(string='Number',default="Draft")
    pan_no = fields.Char(related='partner_id.pan_no', string="Pan No")
    msme = fields.Char(related='partner_id.msme', string="MSME")


    @api.model_create_multi
    def create(self,vals):
        res = super(AccountMove, self).create(vals)
        if res.name:
            if "Draft" in res.name:
                type=""
                today = datetime.today()
                current_month = datetime.strftime(today,'%m')
                current_year = datetime.strftime(today,'%y')
                fiscal =""
                if int(current_month) < 4:
                   fiscal = str(int(current_year)-1) + "-" + current_year
                if int(current_month) > 4:
                    fiscal = current_year +"-"+str(int(current_year) + 1)

                if res.move_type == 'out_invoice':
                    type = "INV"
                if res.move_type == 'in_invoice':
                    type = "BILL"
                if res.move_type == 'out_refund':
                    type = "RINV"
                if res.move_type == 'in_invoice':
                    type = "RBILL"

                seq = self.env['ir.sequence'].next_by_code('custom.account.move')
                res['name']= "SE"+type+"/"+fiscal+"/"+seq
        else:
            type = ""
            today = datetime.today()
            current_month = datetime.strftime(today, '%m')
            current_year = datetime.strftime(today, '%y')
            fiscal = ""
            if int(current_month) < 4:
                fiscal = str(int(current_year) - 1) + "-" + current_year
            if int(current_month) > 4:
                fiscal = current_year + "-" + str(int(current_year) + 1)

            if res.move_type == 'out_invoice':
                type = "INV"
            if res.move_type == 'in_invoice':
                type = "BILL"
            if res.move_type == 'out_refund':
                type = "RINV"
            if res.move_type == 'in_invoice':
                type = "RBILL"

            seq = self.env['ir.sequence'].next_by_code('custom.account.move')
            res['name'] = "SE" + type + "/" + fiscal + "/" + seq
        return res

    # def _post(self, soft=True):
    #     res = super(AccountMove, self)._post(soft=True)
    #     if self.name:
    #         if "Draft" in self.name:
    #             type=""
    #             today = datetime.today()
    #             current_month = datetime.strftime(today,'%m')
    #             current_year = datetime.strftime(today,'%y')
    #             fiscal =""
    #             if int(current_month) < 4:
    #                fiscal = str(int(current_year)-1) + "-" + current_year
    #             if int(current_month) > 4:
    #                 fiscal = current_year +"-"+str(int(current_year) + 1)
    #
    #             if self.move_type == 'out_invoice':
    #                 type = "INV"
    #             if self.move_type == 'in_invoice':
    #                 type = "BILL"
    #             if self.move_type == 'out_refund':
    #                 type = "RINV"
    #             if self.move_type == 'in_invoice':
    #                 type = "RBILL"
    #
    #             seq = self.env['ir.sequence'].next_by_code('custom.account.move')
    #             self.sudo().write({'name':"SE"+type+"/"+fiscal+"/"+seq})
    #     return res
