#!/bin/bash

 
# main stuff
nThreads=$( whiptail --fb --title "Threads" --inputbox 'How many threads?' 0 0 3>&1 1>&2 2>&3 )
case $? in
	  1) clear ; exit 1 ;;
	  2) clear ; exit 1 ;;
	255) clear ; exit 1 ;;
esac

exeCmd=0

if ! [[ $nThreads =~ ^[0-9]+$ ]]
then
    echo "Number of threads must be a positive integer."; exit 1
fi

let i=0 # define counting variable
W=() # define working array
while read -r line; do # process file by file
    let i=$i+1
    W+=("${line%.py} \"\" OFF")
done < <( ls -1 configs/ )

MENU="whiptail --fb --separate-output --title \"List file of directory configs/\" --checklist \"Which datasets to run?\" 0 0 0 ${W[@]} 3>&2 2>&1 1>&3"
# echo $MENU
FILES=$(eval $MENU) # show dialog and store output
# echo $FILES
case $? in
	  1) clear ; exit 1 ;;
	  2) clear ; exit 1 ;;
	255) clear ; exit 1 ;;
esac
if [[ $FILES = '' ]]
then
    whiptail --fb --title 'Error!' --msgbox 'No dataset selected. Aborting...' 12 78 ; clear ; exit 1
fi
  

let j=0 # define counting variable
Q=() # define working array
while read -r line; do # process file by file
	# echo $line    
    Q+=("nohup ./muPhotonRate.py $nThreads configs/$line.py >& ${line%.py}.log & \n")
done < <( sed -e 's/\s\+/\n/g' <<<sed -e 's/^"//' -e 's/"$//' <<<$FILES )
 

whiptail --fb --msgbox "Run:\n\n$(echo " ${Q[@]}")" 0 0 && exeCmd=1
case $? in
	  1) clear ; exit 1 ;;
	  2) clear ; exit 1 ;;
	255) clear ; exit 1 ;;
esac

 

# do the thing
if [ $exeCmd = 1 ]
  then
  	#echo $exeCmd
  	clear
  	echo -e "\n #copy and paste\n"
  	echo " setenv PYTHONUNBUFFERED 1"
    echo -e " ${Q[@]}"
    echo -e "\n\n"
    # eval `echo -e " ${Q[@]}"`
    # echo "$nThreads"
    # echo "$datasets"
    # echo "Vai!"
fi

if [ $exeCmd = 0 ]
  then
	clear
	exit 1
fi


