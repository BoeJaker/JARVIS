#!/bin/bash

arg="$1" ; arg2="$2"

[ "$arg" == "ip" ] && {
	ifconfig -a | egrep -o 'inet addr:[0-9]{3}.[0-9]{3}.[0-9].[0-9]{2}' | sed 's/inet addr://' ; exit
}
[ "$arg" == "server" ] && {
	gnome-terminal -e "python3 -m http.server $arg2" 2>/dev/null &
	exit
}
[ "$arg" == "ipscan" ] && {
	nmap -sn 192.168.0.0/24 | egrep -o '[0-9]{3}.[0-9]{3}.[0-9].[0-9]{2}' ; exit
}
[ "$arg" == "macip" ] && {
	nmap -sP 192.168.0.0/24 >/dev/null && arp -an | grep "$arg2" | awk '{print $2}' | sed  's/[()]//g' ; exit
}

# TODO Add LAN mac adress reverse lookup