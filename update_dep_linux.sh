#! /bin/bash

if [ "$(python3 -V | sed 's/^.* \(.*\)\..*$/\1/')" \< "3.5" ]; then
	echo "JukeBot requires python 3.5.0 or later"
	exit -2
fi

sudo python3 -m pip install --upgrade -r requirements.txt
