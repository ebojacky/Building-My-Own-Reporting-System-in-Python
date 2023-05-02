#!/bin/bash

APPS=/app/ireport
LOGS=/app/ireport/logs
CDRS=/app/ireport/cdrs
CDRSJSON=/app/ireport/cdrs/json
CDRSDONE=/app/ireport/cdrs/done
DBS=/app/ireport/dbs
TEMPHTML=/app/ireport/templates/user_temp_html

if [ $1 == 'status' ]
then
	echo ""
	echo "SFTP LOGS"
	echo "=========="
	tail $LOGS/ireport_sftp.log
	echo ""
	echo "COUNTER LOGS"
	echo "=========="
	tail $LOGS/ireport_counter.log
	echo ""
	echo "MAIN LOGS"
	echo "=========="
	tail $LOGS/ireport_main.log
	echo ""
	echo "LISTENER STATUS"
	echo "=========="
	netstat -an | grep 5050
	echo ""
	echo "SFTP FILE COUNT"
	echo "=========="
	for d in `ls  -r $CDRS | grep -P -e "\d{8}" | head -3`;do
		echo $d = `ls -l $CDRS/$d | wc -l`
	done
	echo ""
	echo "JSON FILE COUNT"
	echo "=========="
	for d in `ls  -r $CDRSJSON | grep -P -e "\d{8}" | head -3`;do
		echo $d = `ls -l $CDRSJSON/$d | wc -l`
	done
	echo ""
	echo "DONE FILE COUNT"
	echo "=========="
	for d in `ls  -r $CDRSDONE | grep -P -e "\d{8}" | head -3`;do
		echo $d = `ls -l $CDRSDONE/$d | wc -l`
	done
	echo ""
	echo "CRON LOGS"
	echo "=========="
	sudo more /var/log/cron | grep ireport | tail -24

fi

pids=$(ps -ef | grep "ireport_*" | grep ".py"|grep -v grep | awk '{print $2}')

if [ $1 == 'stop' ]
then
	for p in $pids;do
		echo Killing $p
		kill $p
		echo "Ireport processes killed"
	done
fi

if [ $1 == 'start' ]
then
	if [ -z "$pids" ]
	then
		echo "Starting Ireport processes"
		python3 $APPS/ireport_sftp.py &
		python3 $APPS/ireport_counter.py &
		python3 $APPS/ireport_main.py &
		echo "Ireport processes started"
	else
		echo "One or more Ireport processes already running. Stop them first."
	fi
fi

if [ $1 == 'cleanup' ]
then
	find $LOGS/* -mtime +14 -type f -exec rm {} \;
	find $DBS/* -mtime +90 -type f -exec rm {} \;
	find $TEMPHTML/* -mtime +3 -type f -exec rm {} \;

	find $CDRS/* -mtime +5 -type f -exec rm {} \;
	find $CDRSJSON/* -mtime +90 -type f -exec rm {} \;
	find $CDRSDONE/* -mtime +90 -type f -exec rm {} \;

	find $CDRS/[0-9]*[0-9] -mtime +5 -type d -exec rmdir {} \;
	find $CDRSJSON/* -mtime +90 -type d -exec rmdir {} \;
	find $CDRSDONE/* -mtime +90 -type d -exec rmdir {} \;
fi
