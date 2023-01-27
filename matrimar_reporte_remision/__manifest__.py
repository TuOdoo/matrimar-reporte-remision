# -*- coding: utf-8 -*-
{
    'name': "Reporte remision",

    'summary': """""",

    'description': """
        
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '14.1',
    'depends': [
        'sale',
        'matrimar_external_dbsource',
        'stock',
        'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_stock_picking_form.xml',
        'views/menu.xml',
        'views/stock_picking.xml',
        'views/template.xml',
        'views/mail_compose_message.xml',
        #'views/res_config_settings_view_form.xml',
        'views/res_company.xml',
        'views/cron.xml',
        'report/report_stock_picking_remision.xml',
    ],
}
