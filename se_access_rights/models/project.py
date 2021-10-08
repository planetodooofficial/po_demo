from odoo import api, fields, models, _,tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class Project(models.Model):
    _inherit = 'project.project'

    def write(self, values):
        res = super(Project, self).write(values)
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for rec in self:
            if user.has_group("se_access_rights.project_manager_user_group"):
                pass
            else:
                if rec.state == 'locked':
                    raise ValidationError(_("Cannot edit locked project"))
        return res