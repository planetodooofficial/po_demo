from odoo import api, models, _
from odoo.exceptions import UserError
from num2words import num2words



class OfferLetterReports(models.AbstractModel):
    _name = 'report.se_hr.pdf_offer_letter_receipt'
    _description = 'Offer Letter Reports'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('se_hr.pdf_offer_letter_receipt')
        getting_values=self.env['offer.letter'].search([('id', '=', docids[0])])
        print(docids)
        total_values_annual=getting_values.ctcs
        ctc_words=num2words(total_values_annual, lang='en_IN').replace(',', '')
        total_values_month=int((getting_values.ctcs)/12)
        basic_annual=int(total_values_annual *0.4)
        basic_month=int(basic_annual/12)
        hra_annual=int(basic_annual/2)
        hra_month=int(hra_annual/12)
        trans_allow_annuals = getting_values.trans_allow_annuals
        trans_allow_month=int((getting_values.trans_allow_annuals)/12)
        medical_allow_annuals = getting_values.medical_allow_annuals
        medical_allow_month=int((getting_values.medical_allow_annuals)/12)
        statutory_bonus_annuals = getting_values.statutory_bonus_annuals
        statutory_bonus_month=int((getting_values.statutory_bonus_annuals)/12)
        other_allow_annual = int(total_values_annual-(basic_annual+hra_annual+getting_values.trans_allow_annuals+getting_values.medical_allow_annuals+getting_values.statutory_bonus_annuals))
        other_allow_month = int((other_allow_annual)/12)
        join_in_bonus=getting_values.join_in_bonus
        total_a_annual=total_values_annual
        plb_month = int((getting_values.plb_annuals)/12)
        plb_annuals = getting_values.plb_annuals
        total_a_b_month=int(total_values_month+plb_month)
        total_a_b_annual=int(total_a_annual+(getting_values.plb_annuals))
        pf_annuals = getting_values.pf_annuals
        pf_month=int((getting_values.pf_annuals)/12)
        grautity=int((basic_month/26)*15)
        total_a_b_c_month = total_a_b_month + pf_month
        total_a_b_c_annual = int(total_a_b_annual + (getting_values.pf_annuals)+grautity)
        total_a_b_c_d_month = total_a_b_c_month
        certi_allows = getting_values.certi_allows
        medical_allows = 15000
        if certi_allows and join_in_bonus :
            total_a_b_c_d_annual = int(total_a_b_c_annual+certi_allows+medical_allows+join_in_bonus)
        elif certi_allows:
            total_a_b_c_d_annual = int(total_a_b_c_annual+certi_allows+medical_allows)
        elif join_in_bonus:
            total_a_b_c_d_annual = int(total_a_b_c_annual+join_in_bonus+medical_allows)
        else:
            total_a_b_c_d_annual = int(total_a_b_c_annual+medical_allows)

        merged= {
            'docs': getting_values,
            'total_values_annual':total_a_annual,
            'total_values_month':total_values_month,
            'basic_month':basic_month,
            'basic_annual':basic_annual,
            'hra_annual':hra_annual,
            'hra_month':hra_month,
            'trans_allow_month':trans_allow_month,
            'trans_allow_annuals':trans_allow_annuals,
            'medical_allow_month':medical_allow_month,
            'medical_allow_annuals':medical_allow_annuals,
            'statutory_bonus_month':statutory_bonus_month,
            'statutory_bonus_annuals':statutory_bonus_annuals,
            'other_allow_annual':other_allow_annual,
            'other_allow_month':other_allow_month,
            'plb_month':plb_month,
            'plb_annuals':plb_annuals,
            'total_a_b_month':total_a_b_month,
            'total_a_b_annual':total_a_b_annual,
            'pf_month':pf_month,
            'pf_annuals':pf_annuals,
            'grautity':grautity,
            'total_a_b_c_month':total_a_b_c_month,
            'total_a_b_c_annual':total_a_b_c_annual,
            'total_a_b_c_d_month':total_a_b_c_d_month,
            'total_a_b_c_d_annual':total_a_b_c_d_annual,
            'certi_allows':certi_allows,
            'medical_allows':medical_allows,
            'join_in_bonus':join_in_bonus,
            'ctc_words':ctc_words,
        }

        return merged