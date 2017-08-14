#! /bin/bash
cd "${0%/*}" # replace with JukeBot directory if the script is moved

function usage() {
	echo "$0 [-hfbcel]"
	echo "  -h  Display this message."
	echo "  -f  Open JukeBot in a foreground process and tee output to CMDlog"
	echo "  -b  Open JukeBot in a background process and redirect output to CMDlog"
	echo "  -c  View the output log (implict if no options specified)"
	echo "  -e  End JukeBot running in a background process"
	echo "  -l  List running bots"
}
if [ "$#" -eq "0" ]; then tail -f CMDlog; exit 0; fi
while getopts :hfbcel o
do
	case "$o" in
	h)	usage
		exit 1;;
	f)	if [ ! -f ".save_pid" ]; then
			sudo python3 JukeBot/JukeBot.py | tee -a CMDlog 2>&1
			exit 0
		else
			echo "JukeBot is already running in the background"
			exit -1;
		fi;;
	b)	if [ ! -f ".save_pid" ]; then
			nohup sudo python3 JukeBot/JukeBot.py >> CMDlog 2>&1 &
			echo $! > .save_pid
			echo "JukeBot started"
			exit $!;
		else
			echo "JukeBot is already running in the background"
			exit -1;
		fi;;
	c)	less +F CMDlog;;
	e)	if [ -f ".save_pid" ]; then
			sudo kill $(cat .save_pid)
			rm .save_pid
			echo "JukeBot stopped"
			exit 0
		else
			echo "No record of JukeBot running in the background"
			exit -1
		fi;;
	l)	if [ ! -f ".save_pid" ]; then
			echo "No record of JukeBot running in the background"
		fi
		ps -xa | grep JukeBot.py | sed '/^.*\(grep\).*$/d'
		;;
	\?)	echo "Invalid option: -$OPTARG"
		usage
		exit 1;;
	esac
done
