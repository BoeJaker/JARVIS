#!/bin/bash

urls="uk.tradingview.com/chart/Hz6O0j76/ \
	uk.tradingview.com/chart/Hz6O0j76/ \
	uk.tradingview.com/chart/Hz6O0j76/ \
	uk.tradingview.com/chart/Hz6O0j76/\
	https://docs.google.com/spreadsheets/d/1WKHhOUw-DlYT6GKX_5VikU3CErNxUrJLh1Z2pVsN-y8/edit#gid=495346032"

x="0"
for url in $urls ; do

	chromium-browser --app="https://$url" & 
	sleep 5
	if [ "$x" == "1" ] ; then
		xdotool key CTRL+SUPER+Left	
	else
		xdotool key CTRL+SUPER+Right
		x="1"
	fi
done
