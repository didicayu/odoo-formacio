{
    'name': "Steam VideoGame Subscription Service",
    'version': '1.0',
    'depends': ['base', 'product', 'steam'],
    'author': "Dídac Cayuela",
    'category': 'VideoGame Subscription',
    'description': """
    optional subscription module for steam
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/subscription_data.xml',
        'data/ir_cron_mail_subscription.xml',
        'views/product_template_views.xml',
    ],
    'application': True,
}
