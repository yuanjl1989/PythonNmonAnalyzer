set WORKSPACE=%cd%
set TIMES=1


set REPORT_TEMPLATE=%WORKSPACE%\ReportTemplate
set TEST_CASE_PATH=%WORKSPACE%\TestCases
set TEST_RESULT_PATH=%WORKSPACE%\TestResults
set SCRIPT_PATH=%WORKSPACE%\Script


if exist %TEST_RESULT_PATH%\ cmd /c rd /S /Q %TEST_RESULT_PATH%\                   
cmd /c mkdir %TEST_RESULT_PATH%


cmd /c copy %REPORT_TEMPLATE%\Summary.html %TEST_RESULT_PATH%\Summary.html
cmd /c copy %REPORT_TEMPLATE%\Details.html %TEST_RESULT_PATH%\Details.html


for /l %%a in (1,1,%TIMES%) do (
	cmd /c jmeter -n -t %TEST_CASE_PATH%\banggo.jmx -l %TEST_RESULT_PATH%\banggo.jtl -L jmeter.util=DEBUG
)


rem ping -n 5 127.1 >nul 2>nul


rem cmd /c %SCRIPT_PATH%\ParseAPIReport.py %TEST_CASE_PATH%\banggo.jmx %TEST_RESULT_PATH%\banggo.jtl %TEST_RESULT_PATH%\Summary.html %TEST_RESULT_PATH%\Details.html 


rem ping -n 10 127.1 >nul 2>nul