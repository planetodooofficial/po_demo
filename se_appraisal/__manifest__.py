{
    'name': 'Secure Eye -Appraisal',
    'version': '14.0.0',
    "category": "Sales,stock,Accounting",
    'summary': 'Sales,Accounting,Delivery',
    "author": "Planet-odoo",
    'website': 'http://www.planet-odoo.com/',
    'depends': ['base','sale','analytic','hr_expense','hr','se_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/roles_mapping_views.xml',
        'wizard/role_mapping_upload_view.xml',
        'views/object_master_view.xml',
        'views/okr_master_view.xml',
        'views/values_master_views.xml',
        'views/pip_meeting_views.xml',
        'views/pip_views.xml',
        'reports/report_pip.xml',
        'views/quarter_master_views.xml',
        'views/quarter_cal.xml',
        'wizard/manager_rating_analytics_view.xml',
        'views/employee_views.xml',
        'views/pms_analytics.xml'
         ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
