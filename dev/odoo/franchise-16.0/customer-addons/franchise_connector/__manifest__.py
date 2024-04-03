{
    'name': "Steam franchise connector",
    'version': '1.0',
    'depends': ['base', 'product'],
    'author': "Dídac Cayuela",
    'category': 'API connector',
    'description': """
    Mock steam api connector
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/config_views.xml',
        'views/iframe_views.xml',
        'views/menu_views.xml',
    ],

    'application': True,
}