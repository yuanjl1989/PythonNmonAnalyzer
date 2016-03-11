#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,shutil,time,datetime,string
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

reload(sys)
sys.setdefaultencoding("utf-8")

myPath=sys.path[0]
parentPath=os.path.dirname(myPath)
listPath=[myPath]
for p in listPath:
	if not p in sys.path:
		sys.path.append(p)

from Common import *



def CreateSummaryImage(listFile,strTitle,listLegend,strImage):
	strYLabel=""
	listData=[]
	listYAxis=[]
	intEnd=100
	intStep=10
	if strTitle.find("CPU_All_User")>-1:
		strYLabel="CPU (%)"
		listData=GetData_MutilFileSingleKey(listFile,listLegend,"CPU_ALL","User%")
	elif strTitle.find("CPU_All_System")>-1:
		strYLabel="CPU (%)"
		listData=GetData_MutilFileSingleKey(listFile,listLegend,"CPU_ALL","Sys%")
	elif strTitle.find("Memory_Free")>-1:
		strYLabel="Memory (%)"
		listTotal=GetData_MutilFileSingleKey(listFile,listLegend,"MEM","memtotal")
		listFree=GetData_MutilFileSingleKey(listFile,listLegend,"MEM","memfree")
		for dictTotal,dictFree in zip(listTotal,listFree):
			dictFree["data"]=[round(float(f)/float(t)*100,2) for t,f in zip(dictTotal["data"],dictFree["data"])]
			listData.append(dictFree)
	elif strTitle.find("Network_Total_IO")>-1:
		strYLabel="Network IO (KB/s)"
		for strFile,strName in zip(listFile,listLegend):
			dictData=FieldData(strFile,"NET")
			listKey=[]
			listValue=[]
			for strKey in dictData.keys():
				if strKey.startswith("eth"):
					listKey.append(strKey)
			for i in range(0,len(dictData[listKey[0]]),1):
				fValue=0.0
				for strKey in listKey:
					fValue=fValue+string.atof(dictData[strKey][i])
				listValue.append(round(fValue,1))
			dict={}
			dict["name"]=strName
			dict["data"]=listValue
			listData.append(dict)
		intEnd=800
		intStep=100

	intTime=GetTotalTime(listFile)
	intDve=intTime/15
	intMod=intTime%15
	if intMod!=0:
		intTime=intTime-intMod+15
	intPeriod=GetTimePeriod(listFile[0])
	listYAxis=GetYAxis(listData,intEnd,intStep)

	fig = plt.figure(figsize=(8,4))
	ax = fig.add_axes([0.1, 0.16, 0.6, 0.75])
	ax.set_title(strTitle,size=14)
	ax.set_xlabel('Time (Seconds)',size=11)
	ax.set_ylabel(strYLabel,size=11)
	ax.set_xlim(0,intTime)
	ax.set_ylim(min(listYAxis),max(listYAxis))

	# ax.spines['top'].set_color('none')
	# ax.spines['right'].set_color('none')
	ax.xaxis.set_ticks_position('bottom')
	for label in ax.xaxis.get_ticklabels():
		label.set_fontsize(7)
	ax.yaxis.set_ticks_position('left')
	for label in ax.yaxis.get_ticklabels():
		label.set_fontsize(7)
	ax.xaxis.set_major_locator(MultipleLocator(intDve+1))
	# ax.xaxis.set_minor_locator(MultipleLocator(1))
	ax.yaxis.set_major_locator(MultipleLocator(intStep))
	# ax.yaxis.set_minor_locator(MultipleLocator(1))

	for data in listData:
		#筛选数据
		# data["data"]=data["data"][0::5]
		# intPeriod=10
		ax.plot(np.array(range(0,len(data["data"])*intPeriod,intPeriod)),np.array(data["data"],dtype=float),label=data["name"])

	# if intMaxPercent>50:
		# ax.plot(np.array([0,intTime]),np.array([50,50]),color ='black',linewidth=1,linestyle="--")

	ax.legend(bbox_to_anchor=(1.0,0.5),loc='center left',borderaxespad=1.0)
	plt.setp(ax.get_legend().get_texts(), fontsize=9)
	fig.autofmt_xdate()
	plt.savefig(strImage)
	
	

def CreatePerformanceReport_Details(strName):
	strReport=dictPath["TestResults"]+strName+".html"
	shutil.copy(dictPath["ReportTemplate"]+"Performance_Details.html",strReport)
	strContent=ReadFileAsString(strReport)

	intIndex=strContent.find("</body>")
	strContent=strContent[:intIndex]+'<br/><h3 align="center">'+strName+'</h3><br/><br/>\n'+strContent[intIndex:]

	for strIP in listIP:
		strNmon=dictPath["TestResults"]+strIP+"/"+strName+".nmon"
		listXAxis=GetXAxis_SingleFileMutilKey(strNmon)

		listTitle=["CPU_All","Memory_Free"]
		intCPUs=GetCPUCount(strNmon)
		for i in range(1,intCPUs+1):
			strTemp="%d"%i
			while len(strTemp)<3:
				strTemp="0"+strTemp
			listTitle.append('CPU'+strTemp)

		for strTitle in listTitle:
			listData=[]
			listYAxis=[]
			intEnd=100
			intStep=10
			if strTitle.find("CPU_All")>-1:
				listData=GetData_SingleFileMutilKey(strNmon,"CPU_ALL",["User%","Sys%","Wait%"])
			elif strTitle.find("CPU")>-1:
				listData=GetData_SingleFileMutilKey(strNmon,strTitle,["User%","Sys%","Wait%"])
			elif strTitle.find("Memory_Free")>-1:
				intTotal=GetData_SingleFileMutilKey(strNmon,"MEM",["memtotal"])[0]["data"][0]
				listFree=GetData_SingleFileMutilKey(strNmon,"MEM",["memfree"])
				for dictFree in listFree:
					dictFree["data"]=[round(float(f)/float(intTotal)*100,2) for f in dictFree["data"]]
					listData.append(dictFree)

			listYAxis=GetYAxis(listData,intEnd,intStep)

			strTitle=strTitle+'_'+strIP.split('.')[3]

			intIndex=strContent.find("</body>")
			strContent=strContent[:intIndex]+'<div id="'+strTitle+'"></div><br/>\n'+strContent[intIndex:]
			intIndex=strContent.find("});")
			strContent=strContent[:intIndex]+'$("#'+strTitle+'").highcharts(Chart('+'"'+strTitle+'",'+str(listXAxis)+','+str(listYAxis)+','+str(listData)+'));\n'+strContent[intIndex:]

	WriteStringToFile(strReport,strContent)
	
	
	
def CreatePerformanceReport():
	CopyDir(dictPath["ReportTemplate"]+"js",dictPath["TestResults"]+"js")
	strReport=dictPath["TestResults"]+"Summary.html"
	shutil.copy(dictPath["ReportTemplate"]+"Performance_Summary.html",strReport)
	strContent=ReadFileAsString(strReport)
	
	dictInterface=GetConfigInterfaceData(dictPath["Config"])

	for strInterface in GetConfigInterfaceName(dictPath["Config"]):
		listNmon=[]
		listName=[]
		for dictScene in dictInterface[strInterface]:
			strName='thread'+dictScene["thread"]+'_loop'+dictScene["loop"]

			strJtlFile=dictPath["TestResults"]+strInterface+'_'+strName+'.jtl'
			listLine=ReadCSVAsList(strJtlFile)
			
			intTotalNum=len(listLine)
			intFailNum=0
			fFailPercent=0
			fReponseTime=0
			qps=0
			fStartTime=0
			fStopTime=0
			for list in listLine:
				if fStartTime==0:
					fStartTime=list[0]
				elif fStartTime>list[0]:
					fStartTime=list[0]

				if fStopTime==0:
					fStopTime=list[0]
				elif fStopTime<list[0]:
					fStopTime=list[0]

				fReponseTime+=int(list[1])

				if not list[7]=='true':
					intFailNum+=1

			fReponseTime=round(float(fReponseTime)/float(intTotalNum),2)

			fStopTime_date=time.strftime('%H-%M-%S',time.localtime(int(fStopTime[:10]))).split('-')
			fStartTime_date=time.strftime('%H-%M-%S',time.localtime(int(fStartTime[:10]))).split('-')
			fCostTime=(int(fStopTime_date[0])-int(fStartTime_date[0]))*60*60+(int(fStopTime_date[1])-int(fStartTime_date[1]))*60+(int(fStopTime_date[2])-int(fStartTime_date[2]))
			fCostTime=fCostTime+(int(fStopTime[-3:])-int(fStartTime[-3:]))/1000.0
			qps=round(float(intTotalNum)/float(fCostTime+fReponseTime/1000),2)

			fFailPercent=round(float(intFailNum)/float(intTotalNum)*100,2)

			intIndex=strContent.find("</tbody>")
			strInsert='<tr><td>'+strInterface+'</td><td>'+dictScene["thread"]+'</td><td>'+dictScene["loop"]+'</td>'
			strInsert+='</td><td>'+str(fReponseTime)+'</td><td>'+str(qps)+'</td><td>'+str(intTotalNum)+'</td>'
			if intFailNum==0:
				strInsert+='<td><font color="green">'+str(intFailNum)+'</font></td><td><font color="green">'+str(fFailPercent)+'</font></td>'
			else:
				strInsert+='<td><font color="red">'+str(intFailNum)+'</font></td><td><font color="red">'+str(fFailPercent)+'</font></td>'
			strInsert+='<td><a href="'+strUrl+strInterface+'_'+strName+'.html">详细信息</a></td></tr>\n'
			strContent=strContent[:intIndex]+strInsert+strContent[intIndex:]

			CreatePerformanceReport_Details(strInterface+'_'+strName)

			listNmon.append(strInterface+'_'+strName+'.nmon')
			listName.append(strName)
	
		intIndex=strContent.find('<td>'+strInterface+'</td>')
		strContent=strContent.replace('<td>'+strInterface+'</td>','')
		strContent=strContent[:intIndex]+'<td align="left" rowspan="'+str(len(listName))+'">'+strInterface+'</td>'+strContent[intIndex:]

		intIndex=strContent.find("</ul>")
		strInsert='<li><h3>'+strInterface+'</h3></li>\n'
		strContent=strContent[:intIndex]+strInsert+strContent[intIndex:]
		
		#----------------------Summary Report for JS-----------------------
		# intPeriod=GetTimePeriod(listNmon[0])
		# intTime=GetTotalTime(listNmon)
		# intDve=intTime/intPeriod
		# intMod=intTime%intPeriod
		# if intMod!=0:
			# intTime=intTime-intMod+intPeriod
		# listXAxis=range(0,intTime,intPeriod)

		# listTitle=["CPU_All_User","CPU_All_System","Memory_Free"]
		# for strTitle in listTitle:
			# strId=strInterface+"_"+strTitle
			# data=GetSummaryData(listNmon,listName,strTitle)
			# listYAxis=GetYAxis(data)
			# intIndex=strContent.find("</li>\n</ul>")
			# strContent=strContent[:intIndex]+'<div id="'+strId+'"></div>'+strContent[intIndex:]
			# intIndex=strContent.find("});")
			# strContent=strContent[:intIndex]+'$("#'+strId+'").highcharts(Chart('+'"'+strTitle+'",'+str(listXAxis)+','+str(listYAxis)+','+str(data)+'));\n'+strContent[intIndex:]
		#----------------------Summary Report for JS-----------------------

		
		#----------------------Summary Report for Matplotlib-----------------------
		
		# 多场景多服务器图
		for strIP in listIP:
			listFile=[]
			for strNmon in listNmon:
				listFile.append(dictPath["TestResults"]+strIP+"/"+strNmon)
				
			listTitle=["CPU_All_User","CPU_All_System","Memory_Free"]
			for strTitle in listTitle:
				strTitle=strTitle+'_'+strIP.split('.')[3]
				strImage=strInterface+'_'+strTitle+'.png'
				CreateSummaryImage(listFile,strTitle,listName,dictPath["TestResults"]+strImage)

				intIndex=strContent.find("</li>\n</ul>")
				strInsert='<img src="'+strUrl+strImage+'"/>'
				strContent=strContent[:intIndex]+strInsert+strContent[intIndex:]
		# 多场景多服务器图

		WriteStringToFile(strReport,strContent)

		#----------------------Summary Report for Matplotlib-----------------------



if __name__=='__main__':
	strUrl=sys.argv[1]
	listIP=sys.argv[2].split(',')
	strTestCase=sys.argv[3]

	dictPath={
			"Dir":parentPath,
			"Config":parentPath+"/TestCases/"+strTestCase+"/TestRunConfig.xml",
			"Script":parentPath+"/Script/",
			"ReportTemplate":parentPath+"/ReportTemplate/",
			"TestCases":parentPath+"/TestCases/"+strTestCase+"/",
			"TestResults":parentPath+"/TestResults/"}		

	CreatePerformanceReport()