#!/usr/bin/env python3.8

import xmlrpc.client

# Odoo server information
ODOO_URL = 'http://localhost:8080'
ODOO_DB = 'mercadona-v16.0-dev'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

# API key obtained from Odoo

# API_KEY = 'be83bfcb1377bbb14c3f38f5a6a338927d54a222' # Res User 'a'
API_KEY = 'a50c8ba20772918cc98708609f995162aa5315b2' # 'Mitchell Admin'

# Odoo common endpoint for XML-RPC
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_URL))

# Authenticate and get user ID
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

# Odoo object endpoint for XML-RPC
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_URL))

# Example: Read some records using the API key
try:
    # Example: Read records from a model
    model_name = 'product.product'
    records = models.execute_kw(ODOO_DB, uid, API_KEY, model_name, 'search_read', [])
    print(str(records).replace(", ", ",\n"))
except Exception as e:
    print("Error:", e)
