#!/bin/bash

SERVICE_NAME="server-monitoring-agentcore-demo"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/server-monitoring-agentcore-demo.service"

case "$1" in
    start)
        sudo cp $SERVICE_FILE /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        sudo systemctl start $SERVICE_NAME
        echo "Service started"
        ;;
    stop)
        sudo systemctl stop $SERVICE_NAME
        echo "Service stopped"
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        echo "Service restarted"
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
