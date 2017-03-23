#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from Common import *
import numpy as np

reload(sys)
sys.setdefaultencoding("utf-8")

myPath=sys.path[0]
parentPath=os.path.dirname(myPath)
listPath=[myPath]
for p in listPath:
	if not p in sys.path:
		sys.path.append(p)

def ReadFileAsString(strFile):
    file_object = open(strFile, 'r')
    try:
        all_the_text = file_object.read()
        listtemp = all_the_text.split("\n")
        listtps = []
        for i in range(0, len(listtemp)):
            if(listtemp[i].lstrip().rstrip()!=""):
				listdatatemp = listtemp[i].split(' ')
				listtps.append(listdatatemp[1])
        return listtps
    finally:
        file_object.close()

def ReadFileGetTime(strFile):
    file_object = open(strFile, 'r')
    try:
        all_the_text = file_object.read()
        listtemp = all_the_text.split("\n")
        listtps = []
        for i in range(0, len(listtemp)):
            if(listtemp[i].lstrip().rstrip()!=""):
				listdatatemp = listtemp[i].split(' ')
				listtps.append(listdatatemp[0])
        return listtps
    finally:
        file_object.close()

def GetTimePeriod(listData):
	if(len(listData[0]["data"]) < 5):
		return len(listData[0]['data'])
	else:
		return 5

def GetTotalTime(listFile):
	intMax=0
	for strFile in listFile:
		listTime=ReadFileGetTime(strFile)
		start=datetime.datetime.strptime(listTime[0],"%H:%M:%S")
		end=datetime.datetime.strptime(listTime[len(listTime)-1],"%H:%M:%S")
		intTime=(end-start).days*24*60*60+(end-start).seconds
		if intTime>intMax:
			intMax=intTime
	return intMax

def GetData_MutilFileSingleKey(listFile,listName):
	listData = []
	for strFile,strName in zip(listFile,listName):
		dictData=ReadFileAsString(strFile)
		dict = {}
		dict["name"] = strName
		dict["data"] = [string.atof(i) for i in list(dictData)]
		listData.append(dict)
	return listData

def CreateSummaryImage(listFile,strTitle,listLegend,strImage):
    strYLabel=""
    listData=[]
    listYAxis=[]
    intEnd=100
    intStep=10

    if strTitle.find("TPS") > -1:
        strYLabel = "TPS (total number/s)"
        listData = GetData_MutilFileSingleKey(listFile, listLegend)

	# intTime这里实际上计算出了x轴时间的刻度数目,整数个15秒
	intTime = GetTotalTime(listFile)
	intDve = intTime / 15
	intMod = intTime % 15
	if intMod != 0:
		intTime = intTime - intMod + 15
	intPeriod = GetTimePeriod(listData)
	listTemp = []
	for data in listData:
		listTemp.append(min(data["data"]))
		listTemp.append(max(data["data"]))
	if(listTemp[1]/listTemp[0]) > 10000:
		intEnd = 10000
		intStep = 2000
	else:
		intEnd = 1000
		intStep = 100
	listYAxis = GetYAxis(listData, intEnd, intStep)


	fig = plt.figure(figsize=(8, 4))
	ax = fig.add_axes([0.1, 0.16, 0.6, 0.75])
	ax.set_title(strTitle, size=14)
	ax.set_xlabel('Time (Seconds)', size=11)
	ax.set_ylabel(strYLabel, size=11)
	ax.set_xlim(0, intTime)
	ax.set_ylim(min(listYAxis), max(listYAxis))

	ax.xaxis.set_ticks_position('bottom')
	for label in ax.xaxis.get_ticklabels():
		label.set_fontsize(7)
	ax.yaxis.set_ticks_position('left')
	for label in ax.yaxis.get_ticklabels():
		label.set_fontsize(7)
	MultipleLocator.MAXTICKS = 10000
	ax.xaxis.set_major_locator(MultipleLocator(intDve + 1))
	ax.yaxis.set_major_locator(MultipleLocator(intStep))

	for data in listData:
		ax.plot(np.array(range(0, len(data["data"]) * intPeriod, intPeriod)), np.array(data["data"], dtype=float),
				label=data["name"])

	ax.legend(bbox_to_anchor=(1.0, 0.5), loc='center left', borderaxespad=1.0)
	plt.setp(ax.get_legend().get_texts(), fontsize=9)		#此句出错RuntimeError: Locator attempting to generate 4112 ticks from -10.0 to 41100.0: exceeds Locator.MAXTICKS
	fig.autofmt_xdate()
	plt.savefig(strImage)

def CreateSummaryImage_MutilServer():
    listTps=[]
    listLegend=[]
    for strPath,listFolder,listFile in os.walk(dictPath["TestResults"]):
        for strIP in listIP:
			listLegend.append('Server_'+strIP)
			for strFile in listFile:
				if strFile.startswith("tps"+"_"+strIP+"_") and strFile.endswith(".log"):
					listTps.append(strPath+strFile)
					break

	listTitle=["TPS"]
	for strTitle in listTitle:
		CreateSummaryImage(listTps,strTitle,listLegend,dictPath["TestResults"]+"_".join(listIP)+"_"+strTitle+'.png')

if __name__=='__main__':
	# print sys.argv[1]
	listIP=sys.argv[1].split(',')
	# print listIP
	dictPath={"TestResults":parentPath+"/TestResults/"}
	# print dictPath
	CreateSummaryImage_MutilServer()

