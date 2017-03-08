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


# CreateSummaryImage(  51*.nmon,CPU_**,  Server_51*,png full path name)
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
		listCached=GetData_MutilFileSingleKey(listFile,listLegend,"MEM","cached")
		listBuffers=GetData_MutilFileSingleKey(listFile,listLegend,"MEM","buffers")
		for dictTotal,dictFree,dictCached,dictBuffers in zip(listTotal,listFree,listCached,listBuffers):
#			for t,f,c,b in zip(dictTotal["data"],dictFree["data"],dictCached["data"],dictBuffers["data"]):
#				print "round(float(f)/float(t+c+b)*100,2)="+str(round(float(f)/float(t+c+b)*100,2))
#				print "round(float(f)/float(t)*100,2)=" + str(round(float(f)/float(t)*100,2))
			dictFree["data"] = [round(float(f) / float(t + c + b) * 100, 2) for t, f, c, b in zip(dictTotal["data"], dictFree["data"], dictCached["data"], dictBuffers["data"])]
#			dictFree["data"]=[round(float(f)/float(t)*100,2) for t,f in zip(dictTotal["data"],dictFree["data"])]
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
		intEnd=50000
		intStep=5000
	elif strTitle.find("Disk_IO")>-1:
		strYLabel="Disk IO (KB/s)"
		for strFile,strName in zip(listFile,listLegend):
			dictWrite=FieldData(strFile,"DISKWRITE")
			listKey = []
			listValue = []
			for strKey in dictWrite.keys():
				if strKey.find("Write")<0:
					listKey.append(strKey)
			for i in range(0,len(dictWrite[listKey[0]]),1):
				fValue=0.0
				for strKey in listKey:
					fValue=fValue+string.atof(dictWrite[strKey][i])
				listValue.append(round(fValue,1))
			dict={}
			dict["name"]=strName+"_DiskWrite"
			dict["data"]=listValue
			listData.append(dict)

			dictRead = FieldData(strFile, "DISKREAD")
			listKey = []
			listValue = []
			for strKey in dictRead.keys():
				if strKey.find("Read")<0:
					listKey.append(strKey)
			for i in range(0, len(dictRead[listKey[0]]), 1):
				fValue = 0.0
				for strKey in listKey:
					fValue=fValue + string.atof(dictRead[strKey][i])
				listValue.append(round(fValue, 1))
			dict = {}
			dict["name"] = strName+"_DiskRead"
			dict["data"] = listValue
			listData.append(dict)
		intEnd=100000
		intStep=20000

	intTime=GetTotalTime(listFile)				#intTime一共有多少时间,单位秒，例如195s
	intDve=intTime/15							#整数个15秒,例如195/15=13
	intMod=intTime%15							#15秒的余数，例如195%15
	if intMod!=0:
		intTime=intTime-intMod+15
	intPeriod=GetTimePeriod(listFile[0])		#
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
#		print len(data["data"])
#		print range(0,len(data["data"])*intPeriod,intPeriod)
#		print np.array(range(0,len(data["data"])*intPeriod,intPeriod))
		ax.plot(np.array(range(0,len(data["data"])*intPeriod,intPeriod)),np.array(data["data"],dtype=float),label=data["name"])

	# if intMaxPercent>50:
		# ax.plot(np.array([0,intTime]),np.array([50,50]),color ='black',linewidth=1,linestyle="--")

	ax.legend(bbox_to_anchor=(1.0,0.5),loc='center left',borderaxespad=1.0)
	plt.setp(ax.get_legend().get_texts(), fontsize=9)
	fig.autofmt_xdate()
	plt.savefig(strImage)


def CreateSummaryImage_MutilServer():
	listNmon=[]
	listLegend=[]
	# print dictPath["TestResults"]
	for strPath,listFolder,listFile in os.walk(dictPath["TestResults"]):
		for strIP in listIP:
			listLegend.append('Server_'+strIP)
			for strFile in listFile:
				# print "1--" + strPath
				# print "2--" + listFolder
				# print "3--" + listFile
				if strFile.startswith(strIP+"_") and strFile.endswith(".nmon"):
					listNmon.append(strPath+strFile)
					break
	# print listNmon

	# listTitle=["CPU_All_User","CPU_All_System","Memory_Free","Network_Total_IO"]
	listTitle=["CPU_All_User","CPU_All_System","Memory_Free","Network_Total_IO","Disk_IO"]
	# listTitle=["Disk_IO"]
	for strTitle in listTitle:
		#CreateSummaryImage(51*.nmon,CPU_**,Server_51*,png full path name)
		CreateSummaryImage(listNmon,strTitle,listLegend,dictPath["TestResults"]+"_".join(listIP)+"_"+strTitle+'.png')



if __name__=='__main__':
	# print sys.argv[1]
	listIP=sys.argv[1].split(',')
	# print listIP
	dictPath={"TestResults":parentPath+"/TestResults/"}
	# print dictPath
	CreateSummaryImage_MutilServer()