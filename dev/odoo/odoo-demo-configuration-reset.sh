#!/bin/bash

ERROR_EXIT=9
ERROR_ARGS=5

DB_ROL_NAME=$1
DB_NAME=$2

function show_usage()
{
    local usage="
    Usage:
        $(basename $0) <usuario base de datos> <nombre base de datos>
    Ej:
        $(basename $0) odoo-0002 demo-cliente
    "
    echo "$usage"
}

# Hace una pregunta y devuelve el resultado de la respuesta
# params:
# $1 -> texto de la pregunta
read_input()
{
    local __resultvar=$2
    local question=$1
    read -p "$question " readed
    if [[ "$__resultvar" ]]
    then
        eval $__resultvar="'$readed'"
    else
        echo "$myresult"
    fi
}

# Modificar parámetros de sistema
function update_system_params()
{
    echo "Modificando parámetros del sistema..."
    # Eliminar database.enterprise_code
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "DELETE FROM ir_config_parameter WHERE key='database.enterprise_code'"
    
    local uuid=$(uuidgen)
    if [ -z $uuid ]
    then
        local uuid='962fa901-54e7-4064-9257-5cd46c24bcb4'
    fi
    # Modificar database.uuid
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='$uuid' WHERE key='database.uuid'"
    # Modificar database.secret
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='$uuid' WHERE key='database.secret'"
    # Modificar ocn.uuid
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='$uuid' WHERE key='ocn.uuid'"
    # Modificar odoo_ocn.project_id
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='000000000000' WHERE key='odoo_ocn.project_id'"
    
    # Eliminar database.expiration_date
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "DELETE FROM ir_config_parameter WHERE key='database.expiration_date'"
    # Modificar database.create_date
    local current_date=$(date '+%Y-%m-%d %H:%M:%S')
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='$current_date' WHERE key='database.create_date'"
    # Modificar database.expiration_reason
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_config_parameter SET value='trial' WHERE key='database.expiration_reason'"
    
    # TODO: actualizar web.base.url, por defecto http://localhost:8080
}

# Modificar configuración de servidores de correo
function update_mail_settings()
{
    echo "Modificando la configuración de servidores de correo..."
    # Modificar servidores de correo saliente ir_mail_server
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_mail_server SET name='disabled_' || name, smtp_host='disabled_' || smtp_host"
    # Modificar servidores de correo entrante fetchmail_server
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE fetchmail_server SET name='disabled_' || name, server='disabled_' || server, state='draft'"
}

function update_cron_settings()
{
    echo "Modificando la configuración de actividades planificadas..."
    # A partir de la version de Odoo v16.0 cambio name(character varying) por cron_name(jsonb)
    # Desactivar la tarea que envía notificaciones a Odoo "Publisher: Update Notification"(evitar que se acabe el período de pruebas en una instancia Enterprise)
    # Odoo < v15.0
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_cron SET active = false where name like '%Publisher:%' || name like '%Update Notification%'"
    # Odoo >= v15.0
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_cron SET active = false where cron_name::text like '%Publisher:%' || cron_name::text like '%Update Notification%'"
        
    # Deshabilitar todos los procesos automáticos excepto los de limpieza '*vacuum'.
    # Odoo < v15.0
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_cron SET active = false where name not like '%acuum%'"
    # Odoo >= v15.0
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE ir_cron SET active = false where cron_name::text not like '%acuum%'"
}

# Modificar los métodos de pago activos
function udpate_payment_acquirer_config()
{
    echo "Modificando métodos de pago..."
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE payment_acquirer SET state='disabled'"
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE payment_acquirer SET environment = 'test'"
}

function update_sii_config()
{
    echo "Modificando entorno de SII..."
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE res_company SET sii_test = true"
}

function update_psync_config()
{
    echo "Modificando configuraciones PSYNC..."
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "update sync set status = false"
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "update sync_subscriber set server_soap_endpoint = '[disabled]' || server_soap_endpoint, status = false"
}

function update_others_config()
{
    echo "Modificando configuraciones Servidores Externos Odoo..."
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "update odoo_server_info set ext_odoo_base_url = '[disabled]' || ext_odoo_base_url, state = 'draft', ext_odoo_dbname = 'dbname', ext_odoo_password = 'dbpassword', ext_equiv_warehouse_id = 0"
}

# Modificar la contraseña del usuario admin
function update_admin_password()
{
    local PYTHON=/usr/bin/python3
    # comprobar existencia de la dependencia passlib
    $PYTHON -m pip freeze | grep passlib
    if [ $? -ne 0 ]
    then
        $PYTHON -m pip install passlib
    fi
    
    #TODO: preguntar si desea modificar la contraseña
    #while(true)
    
    echo "Modificando la contraseña del usuario 'admin'..."
    # Solicitar contraseña al usuario
    read_input "Nueva contraseña: " new_passwd
        
    if [ -z $new_passwd ]
    then
        new_passwd='odoo1234'
    fi

    local encrypted_passwd=$($PYTHON - << EOF
from passlib.context import CryptContext
encrypted=CryptContext(schemes=['pbkdf2_sha512']).encrypt('$new_passwd')
print(encrypted)
EOF
)
    sudo -u $DB_ROL_NAME psql -d $DB_NAME -c "UPDATE res_users SET password='$encrypted_passwd' WHERE login='admin' OR login='rgbadmin'"
}

if [ -z $DB_ROL_NAME ] || [ -z $DB_NAME ] #Comprobar parms
then
        show_usage
        exit $ERROR_ARGS
fi

# Modificar parámetros de sistema
update_system_params

# Modificar configuración de servidores de correo
update_mail_settings

# Modificar configuración de acciones planificadas
update_cron_settings

# Modificar configuración de métodos de pago
udpate_payment_acquirer_config

# Modificar la configuración del SII
update_sii_config

# Modificar la configuración de psync
update_psync_config

# Modificar otras configuraciones
update_others_config

# Actualizar la contraseña de administrador
update_admin_password
