#!/bin/bash
if [ -z "$1" ]; then
    echo "No postgres version specified"
    exit 1
fi
PG_VERSION=$1
PG_BINDIR=/usr/pgsql-${PG_VERSION}/bin
PG_DATADIR=/var/lib/pgsql/${PG_VERSION}/data
PG_SERVICE_NAME="postgresql-${PG_VERSION}"

#init postgres - we shouldn't ever have to do this
if [ -z "$(ls -A ${PG_DATADIR})" ]; then
    su -l postgres -c "${PG_BINDIR}/initdb  --locale='C' --encoding='sql_ascii' --pgdata='${PG_DATADIR}' --auth='trust'"
fi

#fix update error in pg_hba.conf - can remove after 4.0rcs have been out for awhile
if [ -f "${PG_DATADIR}/pg_hba.conf" ]; then
    # Remove #BEGIN-xxx that got jammed up onto previous lines
    sed -i -e 's/\(.\)\(#BEGIN-\)/\1\n\2/' "${PG_DATADIR}/pg_hba.conf"
    # Remove stock pg_hba line that got jammed up on an #END
    sed -i -e 's/#END-esmondlocal/#END-esmond\nlocal/g' "${PG_DATADIR}/pg_hba.conf"
fi

#make sure postgresql is running
/sbin/service ${PG_SERVICE_NAME} status &> /dev/null
if [ $? -ne 0 ]; then
    /sbin/service ${PG_SERVICE_NAME} restart 
    if [ $? -ne 0 ]; then
        echo "Unable to start ${PG_SERVICE_NAME}. Your esmond database may not be initialized"
        exit 1
    fi
fi

#create user if not exists or is an old user
USER_EXISTS=$(su -l postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='esmond'\"" 2> /dev/null)
if [ $? -ne 0 ]; then
    echo "Unable to connect to postgresql to check user. Your esmond database may not be initialized"
    exit 1
fi
OLD_USER_EXISTS=$(su -l postgres -c "psql -tAc \"SELECT 1 FROM pg_authid WHERE rolpassword='md5' || md5('7hc4m1' || rolname)\"" 2> /dev/null)
if [ $? -ne 0 ]; then
    echo "Unable to connect to postgresql to check for old users. Your esmond database may not be initialized"
    exit 1
fi
if [ "$USER_EXISTS" != "1" ] || [ "$OLD_USER_EXISTS" == "1" ]; then
    DB_PASSWORD=$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c32;echo;)
    if [ "$USER_EXISTS" == "1" ]; then
        su -l postgres -c "psql -c \"ALTER ROLE esmond WITH PASSWORD '${DB_PASSWORD}'\"" &> /dev/null
    else
        su -l postgres -c "psql -c \"CREATE USER esmond WITH PASSWORD '${DB_PASSWORD}'\"" &> /dev/null
        su -l postgres -c "psql -c \"CREATE DATABASE esmond\"" &> /dev/null
        su -l postgres -c "psql -c \"GRANT ALL ON DATABASE esmond to esmond\"" &> /dev/null
    fi
    sed -i "s/sql_db_name = .*/sql_db_name = esmond/g" /etc/esmond/esmond.conf
    sed -i "s/sql_db_user = .*/sql_db_user = esmond/g" /etc/esmond/esmond.conf
    sed -i "s/sql_db_password = .*/sql_db_password = ${DB_PASSWORD}/g" /etc/esmond/esmond.conf
    drop-in -n -t esmond - ${PG_DATADIR}/pg_hba.conf <<EOF
#
# esmond
#
# This user should never need to access the database from anywhere
# other than locally.
#
local     esmond          esmond                            md5
host      esmond          esmond     127.0.0.1/32           md5
host      esmond          esmond     ::1/128                md5
EOF
    /sbin/service ${PG_SERVICE_NAME} restart 
    if [ $? -ne 0 ]; then
        echo "Unable to restart ${PG_SERVICE_NAME}. Your esmond database may not be initialized"
    fi
fi

#set esmond env variables
export ESMOND_ROOT=/usr/lib/esmond
export ESMOND_CONF=/etc/esmond/esmond.conf
export DJANGO_SETTINGS_MODULE=esmond.settings

#initialize python
cd $ESMOND_ROOT
. bin/activate

#build esmond tables
python3 esmond/manage.py makemigrations --noinput &> /dev/null
python3 esmond/manage.py migrate --noinput &> /dev/null
