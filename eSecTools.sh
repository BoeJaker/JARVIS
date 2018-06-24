#!/bin/bash
tool=$1 ; inputA=$2

function installDeps(){
	inputA=$1
	dpkg -s $inputA &>/dev/null || { sudo apt-get install -y $inputA ; } && { echo "$inputA dependancy met" ; }
}
function btScan(){
	ERRORLOG="$CWD/bin/btscanerror.txt"
	if [ "$USER" == "root" ]  ; then
		hcitool cc 00:F4:6F:8D:D9:40 &>ERRORLOG
		rssi=$(hcitool rssi 00:F4:6F:8D:D9:40 2>ERRORLOG)
		# BT Error handler ?
		echo "$rssi" | egrep -o '[0-9][0-9]' || echo 0
	else 
		echo "root privilages required" &>ERRORLOG
	fi
}
function networkMap(){
	echo
}
if [ "$tool" == "installDeps" ] ; then
	installDeps $inputA
elif [ "$tool" == "btscan" ] ; then
	btScan
elif [ "$tool" == "nmap" ] ; then
	networkMap 
fi