#!/bin/bash

ERROR_EXIT=9
ERROR_ARGS=5
ERROR_COMMAND=127

# Reset text color
COLOR_OFF='\033[0m'

#Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'

CLIENT_NAME=$1
ODOO_VERSION=$2

DB_NAME=$CLIENT_NAME-v$ODOO_VERSION-dev

OS_CODENAME=$(cat /etc/os-release | grep "VERSION_CODENAME")
OS_CODENAME=${OS_CODENAME#*=}

function show_usage()
{
    usage="
    Usage:
        $(basename $0) <nombre de cliente> <odoo_version>
    Ej:
        $(basename $0) cliente-temp 12.0
    "
    echo "$usage"
}

# Sistemas Debian, Ubuntu
function odoo_system_requiremments_deb()
{
    . /etc/os-release
    if [[ $NAME != "Ubuntu" ]]
    then
        return
    fi
    #PostgreSQL
    sudo apt-get install -y postgresql postgresql-client libpq-dev postgresql-contrib
    
    #sudo apt install ....
    # clean python2
    #sudo apt purge -y python2.7 python2.7-minimal
    sudo apt autoremove -y --purge

    # python2 + python3 + venv
    sudo apt-get install -y python python-dev python-pip python-setuptools
    sudo apt-get install -y python3 python3-dev python3-pip python3-setuptools python3-renderpm
    sudo pip3 install setuptools wheel

    # se valida que no exista el repositorio
    if ! grep -rwnq "deadsnakes/ppa" /etc/apt/
    then
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt-get update
    fi
    # python2.7 y python3.6
    sudo apt-get install -y python2.7 python2.7-dev python2.7-dbg python2.7
    sudo apt-get install -y python3.6 python3.6-dev python3.6-gdb python3.6-distutils
    sudo apt-get install -y python3-virtualenv
    
    # update-alternatives python
    # TODO: versiones de python dinámicas
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 0
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 0
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 0

    # system base
    sudo apt install -y ca-certificates curl dirmngr mc nano bash-completion less
    sudo apt install -y bzip2 zip unzip gettext-base openssh-client telnet xz-utils zlibc
    sudo apt install -y ssh build-essential git

    # dependency libs
    sudo apt install -y fontconfig libfreetype6 libjpeg-turbo8 libx11-6 libxext6 libxml2 libxrender1 libxslt1.1 zlib1g
    sudo apt install -y xfonts-75dpi xfonts-100dpi xfonts-base xfonts-scalable
    sudo apt install -y nodejs node-clean-css node-less

    # c2c / tn extras
    sudo apt install -y antiword ghostscript graphviz poppler-utils
    sudo apt install -y liblcms2-2 libldap-2.4-2 libsasl2-2 libtiff5
    
    # Librerias para necesarias para compatibilidad Odoo
    sudo apt install libncurses5 libncursesw5 libtinfo5

    # development libraries
    sudo apt install -y libevent-dev libjpeg-dev libldap2-dev libsasl2-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev
    sudo apt install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl
    # XPath playground
    # $ xpath -e "//record[@id=',,,']" -e "//field[@name='...']" *.xml
    sudo apt install libxml-xpath-perl
    
    # virtualenv
    sudo apt install -y virtualenv
    
    # wkthml2pdf 0.12.5
    wkhtmltopdf --version | grep '(with patched qt)'
    if [ $? -ne 0 ]
    then
        echo 'Instalando wkthml2pdf 0.12.5...'
        if [ $OS_CODENAME = 'bionic' ]
        then
            # Ubuntu 20.04
            WKHTMLTOPDF_VERSION=0.12.5
            WKHTMLTOPDF_CHECKSUM='db48fa1a043309c4bfe8c8e0e38dc06c183f821599dd88d4e3cea47c5a5d4cd3'
        elif [ $OS_CODENAME = 'focal' ]
        then
            # Ubuntu 22.04
            WKHTMLTOPDF_VERSION=0.12.6-1
            WKHTMLTOPDF_CHECKSUM='ad0264869fe40ccfb91c32e9be7318bfabf3864f6a8a15567f7a38afe4a9a932'
        fi
        
        curl -SLo wkhtmltox-${WKHTMLTOPDF_VERSION}.deb https://github.com/wkhtmltopdf/packaging/releases/download/${WKHTMLTOPDF_VERSION}/wkhtmltox_${WKHTMLTOPDF_VERSION}.${OS_CODENAME}_amd64.deb && echo "${WKHTMLTOPDF_CHECKSUM}  wkhtmltox-${WKHTMLTOPDF_VERSION}.deb" | sha256sum -c - && sudo apt-get install -yqq --no-install-recommends ./wkhtmltox-${WKHTMLTOPDF_VERSION}.deb && sudo rm wkhtmltox-${WKHTMLTOPDF_VERSION}.deb && /usr/local/bin/wkhtmltopdf --version
    fi
    
    if [ $OS_CODENAME = 'bionic' ]
    then
        sudo ln -sf /usr/lib/x86_64-linux-gnu/libffi.so.7 /usr/lib/x86_64-linux-gnu/libffi.so.6
    elif [ $OS_CODENAME = 'focal' ]
    then
        sudo ln -sf /usr/lib/x86_64-linux-gnu/libffi.so.8 /usr/lib/x86_64-linux-gnu/libffi.so.6
    fi
    
    # ------------------------------------------------------------------------------
    # clean packages
    # ------------------------------------------------------------------------------
    sudo apt autoremove --purge -y
    sudo apt clean
}

# crea el fichero de configuración para la instancia
# $1: Nombre del cliente
# $2: Version
# $3: Directorio base
function odoo_conf_creation()
{
    odoo_conf_file=odoo.conf
    odoo_conf="
[options]
admin_passwd = S1sDb4@dev

# addons & data
addons_path = $3/customer-addons, $3/thirdparty-addons, $3/custom-addons, $3/server/addons
data_dir = $3/data

# database
db_host = False
db_port = False
db_user = $USER
db_password = False
dbfilter = ^$DB_NAME$
#db_name = $DB_NAME

# logfiles
log_level = info
log_handler = *:DEBUG,werkzeug:CRITICAL
#logfile=$3/log/odoo.log
#logrotate=true

# xmlrpc
xmlrpc = True
xmlrpc_interface = 127.0.0.1
xmlrpc_port = 9090
longpolling_port = 9091
# Odoo >= 16
#gevent_port = 9091

# workers configuration
#workers = 4
#max_cron_threads = 1
#db_maxconn = 10
#limit_memory_hard = 2684354560
#limit_memory_soft = 2147483648
#limit_request = 8192
#limit_time_cpu = 900
#limit_time_real = 1800
limit_time_cpu = 99999
limit_time_real = 99999

# Connector
#server_wide_modules = web,queue_job
server_wide_modules = web

#[queue_job]
#channels = root:2
"
    echo "$odoo_conf" > $3/$odoo_conf_file
}

function odoo_bin_init_creation()
{
    odoo_bin_file=odoo-bin
    odoo_bin="#!/bin/bash

params=\" -c ./odoo.conf --log-level info \"
sudo -u $USER ./venv/bin/python ./server/odoo-bin \$@ \$params"
    echo "$odoo_bin" > $odoo_bin_file
    sudo chmod +x $odoo_bin_file
}

function odoo_shell_init_creation()
{
    odoo_shell_file=odoo-shell
    odoo_shell="#!/bin/bash

./odoo-bin shell --no-http \$@"
    echo "$odoo_shell" > $odoo_shell_file
    sudo chmod +x $odoo_shell_file
}

#Descargar el código fuente de Odoo
#download_odoo <directorio de Odoo>
function download_odoo()
{
    #forma clasica https://github.com/<user>/<repo>/archive/<brand>.tar.gz
    #BASE_URL=http://github.com/odoo/odoo/archive
    #GitHub API v3
    #https://api.github.com/repos/<user>/<repo>/<format tarball | zipball>/<brand>
    BASE_URL=https://api.github.com/repos/odoo/odoo/tarball
    
    #Comprobar parms
    if [ -z $1 ]
    then
        echo -e "${RED}ERROR: Error al descargar las fuentes de Odoo versión \"$ODOO_VERSION\" ${COLOR_OFF}"
        return $ERROR_ARGS
    fi
    
    ODOO_DIR=$1
    mkdir -p $ODOO_DIR
    curl -L $BASE_URL/$ODOO_VERSION | tar -xz --strip-components=1 -C $ODOO_DIR
}

#Descargar los módulos de la OCA
function download_oca_addons()
{
    #forma clasica https://github.com/<user>/<repo>/archive/<brand>.tar.gz
    #BASE_URL=http://github.com/odoo/odoo/archive
    #GitHub API v3
    #https://api.github.com/repos/<user>/<repo>/<format tarball | zipball>/<brand>
    BASE_URL=https://api.github.com/repos/OCA
    DOWNLOAD_FORMAT=tarball

    OCA_ADDONS=(account-analytic account-closing account-financial-reporting account-financial-tools account-fiscal-rule account-invoicing account-payment account-reconcile donation bank-payment bank-statement-import brand commission community-data-files connector connector-ecommerce contract credit-control crm currency delivery-carrier e-commerce edi hr hr-attendance hr-expense hr-holidays intrastat-extrastat iot l10n-spain maintenance manufacture manufacture-reporting margin-analysis mis-builder partner-contact pms pos product-attribute product-pack product-variant project purchase-reporting purchase-workflow queue reporting-engine sale-promotion sale-reporting sale-workflow server-auth server-backend server-brand server-env server-tools server-ux social stock-logistics-barcode stock-logistics-reporting stock-logistics-warehouse stock-logistics-workflow timesheet web website)

    #Comprobar parms
    if [ -z $1 ]
    then
        echo -e "${RED}ERROR: Error al descargar los addons de la OCA versión \"$ODOO_VERSION\" ${COLOR_OFF}"
        return $ERROR_ARGS
    fi
    
    OCA_ADDONS_DIR=$1
    FORCE_UPDATE=false
    if [[ $2 == "-f" ]]; then FORCE_UPDATE=true; fi
    
    mkdir -p $OCA_ADDONS_DIR

    for((i=0;i<${#OCA_ADDONS[*]};i++))
    do
        echo Descargando ${OCA_ADDONS[$i]}...
        TEMP_DIR=$OCA_ADDONS_DIR/${OCA_ADDONS[$i]}-$ODOO_VERSION
        if [ ! -d $TEMP_DIR ] || [ "$FORCE_UPDATE" = true ]
        then
            mkdir -p $TEMP_DIR
            curl -L $BASE_URL/${OCA_ADDONS[$i]}/$DOWNLOAD_FORMAT/$ODOO_VERSION | tar -xz --strip-components=1 -C $TEMP_DIR
        fi
    done
}

#Se descargan los módulos de RGB
function download_rgb_addons()
{
    BASE_URL=https://api.github.com/repos/rgbconsulting/odoo-addons
    DOWNLOAD_FORMAT=tarball

    #Comprobar parms
    if [ -z $ODOO_VERSION ]
    then
        echo -e "${RED}ERROR: Error al descargar los addons de RGB versión \"$ODOO_VERSION\" ${COLOR_OFF}"
        return $ERROR_ARGS
    fi
    
    RGB_ADDONS_DIR=./addons-lib/rgbconsulting
    mkdir -p $RGB_ADDONS_DIR
    
    curl -L $BASE_URL/$DOWNLOAD_FORMAT/$ODOO_VERSION | tar -xz --strip-components=1 -C $RGB_ADDONS_DIR
}

if [ -z $CLIENT_NAME ] || [ -z $ODOO_VERSION ] #Comprobar parms
then
        show_usage
        exit $ERROR_ARGS
fi

#Instalar dependencias del SO
echo ""
echo "Instalando dependencias del sistema para Odoo..."
odoo_system_requiremments_deb

#Crear estructura de carpetas y ficheros base
echo ""
echo "Creando estructura de carpetas en \"`pwd`/$DEST_DIR\"..."
DEST_DIR=$CLIENT_NAME-$ODOO_VERSION
mkdir $DEST_DIR
cd $DEST_DIR
mkdir -p custom-addons customer-addons thirdparty-addons data/filestore

#Descarga de Odoo y Addons
COMMUNITY_BASE_DIR=/opt/odoo/community
mkdir -p $COMMUNITY_BASE_DIR
OCA_ADDONS_SRC_DIR=$COMMUNITY_BASE_DIR/$ODOO_VERSION/oca
#Descarga de módulos de la oca (addons-lib)
echo ""
echo "Descargando módulos de la OCA para la versión \"$ODOO_VERSION\"..."
#download_oca_addons $OCA_ADDONS_SRC_DIR -f
download_oca_addons $OCA_ADDONS_SRC_DIR
echo "Creando enlaces a los módulos de la OCA en el directorio \"custom-addons/\"..."
ln -sf $OCA_ADDONS_SRC_DIR/*/* custom-addons/

#Descarga de módulos de RGB (addons-lib)
echo ""
echo "Descargando módulos de RGB para la versión \"$ODOO_VERSION\"..."
#download_rgb_addons 

#Creación de ficheros de configuración
echo ""
echo "Creando fichero de configuración \"$(pwd)/odoo.conf\"..."
odoo_conf_creation $CLIENT_NAME $ODOO_VERSION $(pwd)
echo "Creando fichero de configuración \"$(pwd)/odoo-bin\"..."
odoo_bin_init_creation
echo "Creando fichero de configuración \"$(pwd)/odoo-shell\"..."
odoo_shell_init_creation

# Validar existencia de los ficheros del servidor de Odoo(community o enterprise)
# Si no existe, se descarga
echo ""

ODOO_SRC_DIR=$COMMUNITY_BASE_DIR/$ODOO_VERSION/odoo-$ODOO_VERSION
if [ ! -e $ODOO_SRC_DIR ]
then
    echo -e "${YELLOW}WARNING: No se ha encontrado el servidor odoo \"$ODOO_VERSION\" base ${COLOR_OFF}"
    # Community
    mkdir -p $COMMUNITY_BASE_DIR
    echo "Descargando las fuentes del servidor de Odoo \"$ODOO_VERSION\"..."
    download_odoo $ODOO_SRC_DIR
    # Enterprise
fi

#Crear acceso directo a Odoo Base
echo "Creando enlace al servidor de Odoo \"$ODOO_VERSION\"..."
ln -sf $ODOO_SRC_DIR server
if [ $? -eq 0 ]
then
    echo "$(ls -l $(pwd)/server | awk {'print $9 " " $10 " " $11'})"
fi

#Creación del entorno virtual e instalación de dependencias de python para Odoo
echo ""
mkdir venv
if (( $(echo "$ODOO_VERSION > 10.0" | bc -l) ))
then
    if (( $(echo "$ODOO_VERSION > 11.0" | bc -l) ))
    then
        python3.8 --version
        if [ $? -eq 0 ]
        then
            echo "Instalando virtualenv $(python3.8 --version)..."
            virtualenv --python=python3.8 venv
        else
            echo -e "${RED}ERROR: Se debe instalar python3.8 ${COLOR_OFF}"
        fi
    else
        python3.6 --version
        if [ $? -eq 0 ]
        then
            echo "Instalando virtualenv $(python3.6 --version)..."
            virtualenv --python=python3.6 venv
        else
            python3 --version
            if [ $? -eq 0 ]
            then
                echo "Instalando virtualenv $(python3 --version)..."
                virtualenv --python=python3 venv
            else
                echo -e "${RED}ERROR: Se debe instalar python3 ${COLOR_OFF}"
            fi
        fi
    fi
else
    python2 --version
    if [ $? -eq 0 ]
    then
        echo "Instalando virtualenv $(python2 --version)..."
        virtualenv --python=python2 venv
    else
        echo -e "${RED}ERROR: Se debe instalar python2 ${COLOR_OFF}"
    fi
fi

echo ""
echo "Actualizando pip en el entorno virtual de Python..."
venv/bin/python -m pip install --upgrade pip

echo ""
echo "Instalando las dependencias de python del servidor de Odoo \"$ODOO_VERSION\"..."
echo "$(ls -l $(pwd)/server | awk {'print $9 " " $10 " " $11'})"
venv/bin/python -m pip install -r server/requirements.txt

echo ""
echo "Instalando las dependencias de python de los repositorios de la OCA para Odoo \"$ODOO_VERSION\"..."
for dir in $OCA_ADDONS_SRC_DIR/*
do
    requirements_file="${dir}/requirements.txt"
    if [ -e $requirements_file ]
    then
        venv/bin/python -m pip install -r $requirements_file
    fi
done


#Crear usuario de BD
echo "Creando el usuario de base de datos \"$USER\""
sudo -u postgres createuser -dS $USER

#Crear la base de datos <cliente>-<version odoo>-dev
#Ej: 
#   createdb client1-v12.0-dev
echo ""
echo "Creando la base de datos \"$DB_NAME\""
sudo -u $USER psql -d template1 -c "CREATE DATABASE \"$DB_NAME\" TEMPLATE template0 LC_COLLATE 'C'"

echo ""
echo "Acciones post-instalación:"
echo -e "${YELLOW}"
echo "1- Instalar los requisitos de python a partir del \"venv\" del cliente \"$CLIENT_NAME\""
echo "En el vps del cliente ejecutar:"
echo "    /opt/odoo/sites/0001/venv/bin/python -m pip freeze"
echo "En Local ejecutar:"
echo "    $(pwd)/venv/bin/python -m pip -install -r client-pip-freeze.txt"
echo "2- Restaurar la copia de base de datos en la BD creada"
echo "Ejecutar:"
echo "    sudo -u $USER psql -d $DB_NAME < BACKUP.sql > /dev/null sustituyendo \"BACKUP.sql\" por el nombre del fichero de copia de BD"
echo "3- Copiar los módulos de la OCA y RGB necesarios para el cliente \"$CLIENT_NAME\""
echo "4- Clonar el repositorio de Gitea para el cliente \"$CLIENT_NAME\" en el directorio \"customer-addons\""
echo -e "${COLOR_OFF}"
