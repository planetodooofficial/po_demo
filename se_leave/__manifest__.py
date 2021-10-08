{
    'name': 'Secure Eye-Leave',
    'version': '14.0.0',
    "category": "Attendance and Leave",
    'summary': 'Attendance and Leave',
    "author": "Planet-odoo",
    'website': 'http://www.planet-odoo.com/',
    'depends': ['hr','hr_holidays','hr_attendance','se_hr','resource'],
    'data': [
        'security/ir.model.access.csv',
        'security/se_leave_security.xml',
        'views/employee_view.xml',
        'views/leave_views.xml',
        'views/hr_attendance_inherited_view.xml',
        'wizard/leave_report_wizard.xml',
        'wizard/import_holidays_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
