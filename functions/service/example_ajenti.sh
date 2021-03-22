#!/bin/sh

### BEGIN INIT INFO
# Provides:          ajenti
# Required-Start:    $network $syslog $local_fs
# Required-Stop:     $network $syslog $local_fs
# Should-Start:      $local_fs
# Should-Stop:       $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Ajenti
# Description:       Ajenti administration frontend
### END INIT INFO

if [ -e /lib/lsb/init-functions ]; then
    . /lib/lsb/init-functions
    
    log_success() {
        log_success_msg "$1"
    }

    log_failure() {
        log_failure_msg "$1"
    }
else
    . /etc/rc.d/init.d/functions

    log_success() {
        echo_success
        echo "$1"
    }

    log_failure() {
        echo_failure
        echo "$1"
    }
fi

NAME=Ajenti
DAEMON=/usr/bin/ajenti-panel
PIDFILE=/var/run/ajenti.pid

case "$1" in
    start)
        echo "Starting $NAME:"
        export LC_CTYPE=en_US.UTF8

        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            log_failure "already running"
            exit 1
        fi
        if $DAEMON -d ; then
            log_success "started"
        else
            log_failure "failed"
        fi
        ;;
    stop)
        echo "Stopping $NAME:"
        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            killproc -p $PIDFILE $DAEMON
            /bin/rm -rf $PIDFILE
            log_success "stopped"
        else
           log_failure "not running"
        fi
        ;;
    restart)
          $0 stop && sleep 2 && $0 start
        ;;
     status)
        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            log_success "$NAME is running"
        else
            log_success "$NAME is not running"
           fi
          ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1 
esac

exit 0
