#!/bin/bash

CPU_THRESHOLD=90
MEM_THRESHOLD=90
DISK_THRESHOLD=90

DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1419602714400129035/7eVTf2l9JybO5_E5aAy0fMNOqgly3bWvGFJMlJcHw29q0P5KaJAAFPuHuAi0dVhanLzq"

HOSTNAME=$(hostname)

function send_alert {
    MESSAGE=$1
    PAYLOAD="{\"content\":\"**ALERT:** $MESSAGE\"}"
    curl -H "Content-Type: application/json" -X POST -d "$PAYLOAD" "$DISCORD_WEBHOOK_URL"
}

CPU_IDLE=$(top -l 1 | grep "CPU usage" | awk '{print $7}' | sed 's/%//')
CPU_USAGE=$(echo "100.0 - $CPU_IDLE" | bc -l)

if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    send_alert "High CPU usage on $HOSTNAME: ${CPU_USAGE}%"
fi

MEM_USAGE=$(vm_stat | perl -ne '/page size of (\d+)/ && ($size = $1); /Pages free:\s+(\d+)/ && ($free = $1); /Pages active:\s+(\d+)/ && ($active = $1); /Pages inactive:\s+(\d+)/ && ($inactive = $1); /Pages wired down:\s+(\d+)/ && ($wired = $1); END { $total = $active + $inactive + $wired + $free; $used = $active + $inactive + $wired; printf("%.0f\n", $used / $total * 100) }')

if (( $(echo "$MEM_USAGE > $MEM_THRESHOLD" | bc -l) )); then
    send_alert "High Memory usage on $HOSTNAME: ${MEM_USAGE}%"
fi

df -H | grep '^/dev/' | awk '{ print $5 " " $1 }' | while read -r output;
do
    USAGE=$(echo "$output" | awk '{ print $1}' | sed 's/%//g')
    PARTITION=$(echo "$output" | awk '{ print $2 }')
    
    if [ "$USAGE" -gt "$DISK_THRESHOLD" ]; then
        send_alert "High Disk usage on $HOSTNAME: $PARTITION is ${USAGE}% full"
    fi
done