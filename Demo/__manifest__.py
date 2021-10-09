{
    'name': 'Walplast Demo ',
    'version': '14.0.0',
    "category": "Sales",
    'summary': 'Sales,',
    "author": "Planet-odoo",
    'website': 'http://www.planet-odoo.com/',
    'depends': ['base','sale','analytic','hr_expense','hr','product','se_custom','mail','bi_hr_employee_orientation','hr_resignation'],
    'data': [
        'views/alert_mail_cron.xml',
        'views/mail_department_view.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
