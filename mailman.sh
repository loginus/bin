#!/bin/bash

#################### ISAR ##############################
while getopts  "g:p:" FLAG
do
        case $FLAG in
                "g") GROUP="$OPTARG" ;;
                "p") PASSWORD="$OPTARG" ;;
                *) exit
        esac
done
if [[ -z $GROUP || -z $PASSWORD ]]
then
	echo "parameters missing"
	exit
fi

shift 4

curl -k --cookie cookies.txt --cookie-jar cookies.txt --user-agent Mozilla/4.0 --data "adminpw=$PASSWORD" http://listserv.comarch.pl/mailman/admin/$GROUP/ -v
for USER in $@
do
	curl -k --cookie cookies.txt --cookie-jar cookies.txt --user-agent Mozilla/4.0 --data "send_welcome_msg_to_this_batch=1&subscribees=$USER" http://listserv.comarch.pl/mailman/admin/$GROUP/members -v
done
