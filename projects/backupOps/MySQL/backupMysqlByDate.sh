#!/usr/bin/env bash
# Function description:
# Backup MySQL databases for each, backup schema and schema with data in one action.

# Usage:
# bash BackupMysqlByDate.sh

# Birth Time:
# 2016-06-24 17:44:43.895515929 +0800

# Author:
# Open Source Software written by 'Guodong Ding <liuhongda@didiglobal.com>'
# Blog: http://dgd2010.blog.51cto.com/
# Github: https://github.com/DingGuodong

# Others:
# crontabs -- configuration and scripts for running periodical jobs
# SHELL=/bin/bash
# PATH=/sbin:/bin:/usr/sbin:/usr/bin
# MAILTO=root
# HOME=/
# For details see man 4 crontabs
# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
# m h  dom mon dow   command
# execute on 11:59 per sunday
# 59 11 * * */0 /path/to/BackupMysqlByDate.sh >/tmp/log_backup_mysql_$(date +"\%Y\%m\%d\%H\%M\%S").log
# or
# execute on 23:59 per day
# 59 23 * * * /path/to/BackupMysqlByDate.sh >/tmp/log_backup_mysql_$(date +"\%Y\%m\%d\%H\%M\%S").log

USER="`id -un`"  # $USER is also available
LOGNAME="$USER"
if [[ ${UID} -ne 0 ]]; then
    echo "WARNING: Running as a non-root user, \"$LOGNAME\". Functionality may be unavailable. Only root can use some commands or options"
fi

old_PATH=$PATH
declare -x PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"

mysql_host=127.0.0.1
mysql_port=3306
mysql_username=dev
mysql_password=dev
mysql_backup_remote=true
mysql_basedir=/usr/local/mysql
save_old_backups_for_days=5
mysql_bin_mysql=${mysql_basedir}/bin/mysql
mysql_bin_mysqldump=${mysql_basedir}/bin/mysqldump
mysql_backup_dir=/data/backup/db/mysql

date_format_type_dir=$(date +%Y-%m-%d)
date_format_type_file=$(date +%Y%m%d%H%M%S)

echo "------------------------------------------------------------------------"
echo "=> do backup scheduler start at $(date +%Y%m%d%H%M%S)"

# TODO, check user privileges
# check user if have 'RELOAD,EVENT' privileges,etc
# backup role
# GRANT ALTER,ALTER ROUTINE,CREATE,CREATE ROUTINE,CREATE TEMPORARY TABLES,CREATE VIEW,DELETE,DROP,EXECUTE,INDEX,INSERT,LOCK TABLES,SELECT,UPDATE,SHOW VIEW,RELOAD,EVENT ON *.* TO 'dev'@"%";
# FLUSH PRIVILEGES;

[[ -d ${mysql_basedir} ]] && mysql_datadir=${mysql_basedir}/data || mysql_datadir=/var/lib/mysql
[[ -x ${mysql_bin_mysql} ]] || mysql_bin_mysql=mysql
[[ -x ${mysql_bin_mysqldump} ]] || mysql_bin_mysqldump=mysqldump

if [[ ! -d ${mysql_datadir} ]] ; then
    echo "WARNING: mysql datadir is not standard(this maybe a mistake) or mysql server is not installed on local filesystem."
fi

if [[ ! -x ${mysql_bin_mysql} ]] ;then
    echo "mysql: command not found "
    exit 1
fi

if [[ ! -x ${mysql_bin_mysqldump} ]]; then
    echo "mysqldump: command not found "
    exit 1
fi

[[ -d ${mysql_backup_dir}/${date_format_type_dir} ]] || mkdir -p ${mysql_backup_dir}/${date_format_type_dir}

mysql_databases_list=""
if [[ -d ${mysql_datadir} ]] && [[ "x${mysql_backup_remote}" != "xtrue" ]]; then
    mysql_databases_list=`ls -p ${mysql_datadir} | grep / |tr -d /`
else
    mysql_databases_list=$(${mysql_bin_mysql} -h${mysql_host} -P${mysql_port} -u${mysql_username} -p${mysql_password} \
    --show-warnings=FALSE -e "show databases;" 2>/dev/null | grep -Eiv '(^database$|information_schema|performance_schema|^mysql$)')
fi

if [[ "x${mysql_databases_list}" == "x" ]]; then
    echo "no database is found to backup, aborted! "
    exit 1
fi

saved_IFS=$IFS
IFS=' '$'\t'$'\n'
for mysql_database in ${mysql_databases_list};do
    ${mysql_bin_mysqldump} --host=${mysql_host} --port=${mysql_port} --user=${mysql_username} --password=${mysql_password}\
        --routines --events --triggers --single-transaction --flush-logs \
        --ignore-table=mysql.event --databases ${mysql_database} 2>/dev/null | \
        gzip > ${mysql_backup_dir}/${date_format_type_dir}/${mysql_database}-backup-${date_format_type_file}.sql.gz

    [[ $? -eq 0 ]] && echo "${mysql_database} backup successfully! " || \
        echo "${mysql_database} backup failed! "
    /bin/sleep 1

    ${mysql_bin_mysqldump} --host=${mysql_host} --port=${mysql_port} --user=${mysql_username} --password=${mysql_password} \
         --routines --events --triggers --single-transaction --flush-logs \
         --ignore-table=mysql.event --databases ${mysql_database} --no-data 2>/dev/null | \
         gzip > ${mysql_backup_dir}/${date_format_type_dir}/${mysql_database}-backup-${date_format_type_file}_schema.sql.gz

    [[ $? -eq 0 ]] && echo "${mysql_database} schema backup successfully! " || \
        echo "${mysql_database} schema backup failed! "
    /bin/sleep 1
done
IFS=${saved_IFS}

save_days=${save_old_backups_for_days:-10}
need_clean=$(find ${mysql_backup_dir} -maxdepth 1 -ctime +${save_days} -exec ls '{}' \;)
# if [[ ! -z ${need_clean} ]]; then
if [[ "x${need_clean}" != "x" ]]; then
    find ${mysql_backup_dir} -maxdepth 1 -ctime +${save_days} -exec rm -rf '{}' \;
    echo "old backups have been cleaned! "
else
    echo "nothing can be cleaned, skipped! "
fi

echo "=> do backup scheduler finished at $(date +%Y%m%d%H%M%S)"
echo -e "\n\n\n"

declare -x PATH=${old_PATH}
