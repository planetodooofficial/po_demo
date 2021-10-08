{
    'name': 'SE Access Rights',
    'version': '14.0.0',
    "category": "Access Rights",
    'summary': 'Access Rights',
    "author": "Planet-odoo",
    'website': 'http://www.planet-odoo.com/',
    'depends': ['base','sale','analytic','hr_expense','hr','hr_timesheet','maintenance','product','hr_recruitment', 'project','sale_project','purchase','mail','tds_withholding_tax_cv_14e','hr_maintenance','hr_holidays','sale_timesheet','hr_attendance','hr_payroll_community','se_custom'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/project_view.xml',
         ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
