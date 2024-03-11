import xmlrpc.client

url = 'http://localhost:8080'
db = 'mercadona-v16.0-dev'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print('Version info: ' + str(common.version()))

uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
# result = models.execute_kw(db, uid, password, 'project.project', 'update_show_image', [''])

# Get all the projects
project_ids = models.execute_kw(db, uid, password, 'project.project', 'search', [[]])

for project_id in project_ids:
    project = models.execute_kw(db, uid, password, 'project.project', 'read', [project_id])

    # current_show = project[0]['show_image']

    show = (project_id % 2 == 0)

    # Write new result
    models.execute_kw(db, uid, password, 'project.project', 'write', [[project_id], {'show_image': show}])

    print('Project with id ' + str(project_id) + ' now has [show_image]: ' + str(show))
