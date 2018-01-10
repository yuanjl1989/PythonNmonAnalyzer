#!/bin/sh


URL=$1
IPADDRESSES=$2
PROJECT=$3



WORKSPACE=${PWD}
REPORT_TEMPLATE=$WORKSPACE/ReportTemplate
TEST_CASE_PATH=$WORKSPACE/TestCases
TEST_RUN_PATH=$WORKSPACE/TestRun
TEST_RESULT_PATH=$WORKSPACE/TestResults
SCRIPT_PATH=$WORKSPACE/Script
NMONRESULT_PATH=/home/stress


# Generate report
python $SCRIPT_PATH/GeneratePerformanceReport.py $URL $IPADDRESSES $PROJECT


ping -c 10 127.1 >nul 2>nul
