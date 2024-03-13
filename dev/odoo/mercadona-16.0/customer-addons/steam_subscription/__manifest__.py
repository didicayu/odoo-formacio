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
        'views/product_template_views.xml',
    ],
    'application': True,
}
