{
    'name': "Steam VideoGame Store",
    'version': '1.0',
    'depends': ['base', 'product', 'point_of_sale'],
    'author': "Dídac Cayuela",
    'category': 'VideoGame Store',
    'description': """
    Mock steam website
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/language_views.xml',
        'views/tag_views.xml',
        'views/videogame_views.xml',
        'views/key_views.xml',
        'views/users_views.xml',
        'views/steam_menus.xml',
        'views/signup_template.xml',
        'views/library_template.xml',
        'views/game_details_template.xml',
        'views/payment_confirmation_template.xml',
        'views/email_template_api_key.xml',
    ],
    'assets': {
            'point_of_sale.assets': [
                'steam/static/src/xml/ProductItemWithStock.xml',
                'steam/static/src/stock_pos.js',
            ]
        },

    'application': True,
}
