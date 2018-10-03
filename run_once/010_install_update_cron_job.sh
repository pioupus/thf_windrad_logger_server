 #!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
 
croncmd="python $SCRIPTPATH/../update/do_update.py > $HOME/update_cron_log.log 2>&1"

cronjob="*/15 * * * * $croncmd"

( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab - 



