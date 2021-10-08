from odoo import api, fields, models, _,tools

class AccessMaster(models.Model):
    _inherit = 'res.users'

    assign_role = fields.Many2many('access.rights.master', 'access_master_group_table', 'asscess_id', 'user_id', string='Role')

    # @api.model
    # def create(self, vals):
    #     res = super(AccessMaster, self).create(vals)
    #
    #
    #
    #     return res



    def write(self, values):
        res = super(AccessMaster, self).write(values)
        if values.get('assign_role'):
            # for id in values.get('assign_role')[0][2]:
            #     roles = self.env['access.rights.master'].search([('id','=',id)])
            role_ids = []
            for role in self.assign_role:
                # for right in role.right_ids:
                for right in role.right_ids:
                    role_ids.append(right.id)
            
            self.groups_id = [(6,0, role_ids)]

        return res