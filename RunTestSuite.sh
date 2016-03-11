#!/bin/sh


URL=$1
IPADDRESSES=$2
PROJECT=$3


sTime=30
cNum=150


WORKSPACE=${PWD}
REPORT_TEMPLATE=$WORKSPACE/ReportTemplate
TEST_CASE_PATH=$WORKSPACE/TestCases
TEST_RUN_PATH=$WORKSPACE/TestRun
TEST_RESULT_PATH=$WORKSPACE/TestResults
SCRIPT_PATH=$WORKSPACE/Script
NMONRESULT_PATH=/home/stress


# Get ip addresses
OLD_IFS="$IFS" 
IFS="," 
IPARR=($IPADDRESSES) 
IFS="$OLD_IFS" 

# Cleanup .nmon file from server
for ip in ${IPARR[@]} 
do
	ssh root@$ip 'rm -f /home/stress/*.nmon'
done

# Clear TestResults path and TestRun path
if [ -d $TEST_RESULT_PATH ]; then rm -rf $TEST_RESULT_PATH; fi
mkdir $TEST_RESULT_PATH

if [ -d $TEST_RUN_PATH ]; then rm -rf $TEST_RUN_PATH; fi
mkdir $TEST_RUN_PATH

# Generate Test Plan files
python $SCRIPT_PATH/GenerateTestPlanFile.py $PROJECT

# Run each .jmx file in 
for fileFullName in `ls $TEST_RUN_PATH`:
do
	name=${fileFullName%.*}
	
	# Kill nmon, re-start nmon
	for ip in ${IPARR[@]} 
	do 		
		ssh -n $ip 'ps -ef | grep nmon | grep -v grep | cut -c 9-15 | xargs kill -s 9'
		ssh -n $ip "/home/stress/nmon -F ${name}.nmon -t -m /home/stress -s ${sTime} -c ${cNum}"
	done	
	
	sleep 5
	jmeter -n -t $TEST_RUN_PATH/$name.jmx -l $TEST_RESULT_PATH/$name.jtl -L jmeter.until=DEBUG
	sleep 120
	
	# Kill nmon	
	for ip in ${IPARR[@]} 
	do 
		ssh -n $ip 'ps -ef | grep nmon | grep -v grep | cut -c 9-15 | xargs kill -s 9'
	done	
done

# Get .nmon file from all tested servers
for ip in ${IPARR[@]} 
do 
	mkdir $TEST_RESULT_PATH/$ip
	scp -r root@$ip:$NMONRESULT_PATH/*.nmon $TEST_RESULT_PATH/$ip
done

# Generate report
python $SCRIPT_PATH/GeneratePerformanceReport.py $URL $IPADDRESSES $PROJECT


ping -c 10 127.1 >nul 2>nul
