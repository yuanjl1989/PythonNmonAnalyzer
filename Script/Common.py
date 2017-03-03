#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,os,shutil,string,datetime
from xml.etree import ElementTree



##---------------------Common file---------------------
def ReadFileAsString(strFile):
	file=open(strFile,"r")
	strContent=file.read()
	file.close()
	return strContent

def ReadFileAsList(strFile):
	file=open(strFile,"r")
	listLine=file.readlines()
	file.close()
	return listLine

def WriteStringToFile(strFile,strContent):
	file=open(strFile,"w")
	file.write(strContent)
	file.close()
##---------------------Common file---------------------


##---------------------XML file---------------------
def GetXmlElements(strFile,strXpath):
	tree=ElementTree.parse(strFile)
	root=tree.getroot()
	elements=root.findall(strXpath)
	return elements

def GetXmlElement(strFile,strXpath):
	elements=GetXmlElements(strFile,strXpath)
	return elements[0]

def GetXmlElement_Attributes(element):
	return element.attrib

def GetXmlElement_Attribute(element,strAttribute):
	return element.attrib[strAttribute]

def GetXmlElement_Text(element):
	return element.text

def SetXmlElements_Attribute(strFile,strXpath,strAttribute,strValue):
	tree=ElementTree.parse(strFile)
	root=tree.getroot()
	elements=root.findall(strXpath)
	for element in elements:
		element.set(strAttribute,strValue)
	tree.write(strFile)

def SetXmlElement_Attribute(strFile,strXpath,strAttribute,strValue):
	tree=ElementTree.parse(strFile)
	root=tree.getroot()
	elements=root.findall(strXpath)
	elements[0].set(strAttribute,strValue)
	tree.write(strFile)

def SetXmlElement_Text(strFile,strXpath,strText):
	tree=ElementTree.parse(strFile)
	root=tree.getroot()
	elements=root.findall(strXpath)
	elements[0].text=strText
	tree.write(strFile)
##---------------------XML file---------------------	


##---------------------CVS file---------------------
def ReadCSVAsList(strFile):
	listLine=[]
	for strLine in ReadFileAsList(strFile):
		strLine=strLine.replace("\n","")
		listLine.append(strLine.split(","))
	return listLine
##---------------------CVS file---------------------


##---------------------Regex---------------------listData=FindDataByRegex(strFile,r'-s (.*) -c')
def FindDataByRegex(strFile,pattern):
	listData=re.findall(pattern,ReadFileAsString(strFile))
	return listData
##---------------------Regex---------------------


##---------------------Zip list---------------------
def ConvertRowToColumn(listKey,listValue):
	dictData={}
	listValue=zip(*listValue)
##	listvalue=map(list,zip(*listValue))
	for key,value in zip(listKey,listValue):
		dictData[key]=value
	return dictData
##---------------------Zip list---------------------


##---------------------Dir---------------------	
def DeleteDir(dir):
	while os.path.exists(dir):
		shutil.rmtree(dir,True) 

def CreateDir(dir):
	DeleteDir(dir)
	os.makedirs(dir)

def CopyDir(sourDir,destDir):
	DeleteDir(destDir)
	shutil.copytree(sourDir,destDir)
##---------------------Dir---------------------


##---------------------Get data of TestRunConfig.xml---------------------
def GetConfigInterfaceName(strConfig):
    listInterface=[]
    for eInterface in GetXmlElements(strConfig,'.//interface'):
        strInterface=GetXmlElement_Attribute(eInterface,'name')
        listInterface.append(strInterface)
    return listInterface

def GetConfigInterfaceData(strConfig):
	dictInterface={}
	for strInterface in GetConfigInterfaceName(strConfig):
		listScene=[]
		eScene=GetXmlElements(strConfig,'.//interface[@name="'+strInterface+'"]/scene')
		i=1
		while i<=len(eScene):
			dictScene={}
			for e in GetXmlElements(strConfig,'.//interface[@name="'+strInterface+'"]/scene['+str(i)+']/*'):
				dictScene[e.tag]=GetXmlElement_Text(e)
			listScene.append(dictScene)
			i+=1
		dictInterface[strInterface]=listScene
	return dictInterface
##---------------------Get data of TestRunConfig.xml---------------------


##---------------------Get data of nmon file---------------------
def FieldData(strFile,strField,listKey=[]):
	pattern=r''+strField+',(.*)\n';
	listData=FindDataByRegex(strFile,pattern)
	listValue=[]
	# listData的第一个元素作为列名，其他的作为数据
	if listKey==[]:
		listKey=listData[0].split(",")
		for data in listData[1:]:
			listValue.append(data.split(","))
	# 以listKey为列名，listData的所有元素作为数据
	else:
		for data in listData:
			listValue.append(data.split(","))
	dictData=ConvertRowToColumn(listKey,listValue)
	return dictData

# 单个文件多条不同类型的数据线
def GetData_SingleFileMutilKey(strFile,strField,listKey):
	listData=[]
	dictData=FieldData(strFile,strField)
	for strKey in listKey:
		dictTemp={}
		dictTemp["name"]=strKey
		dictTemp["data"]=[string.atof(i) for i in list(dictData[strKey])]
		listData.append(dictTemp)
	return listData

# 多个文件多条相同类型的数据线
def GetData_MutilFileSingleKey(listFile,listName,strField,strKey):
	listData=[]
	for strFile,strName in zip(listFile,listName):
		dictData=FieldData(strFile,strField)
		dict={}
		dict["name"]=strName
		dict["data"]=[string.atof(i) for i in list(dictData[strKey])]
		listData.append(dict)
	return listData

# 单个文件的时间日期X轴
def GetXAxis_SingleFileMutilKey(strFile):
	# dictData=GetFieldData(strFile,"ZZZZ",["index","time","date"])
	# listXAxis=list(dictData["time"])
	# return listXAxis
	dictData=FieldData(strFile,"ZZZZ",["index","time","date"])
	listXAxis=[]
	for date,time in zip(list(dictData["date"]),list(dictData["time"])):
		listXAxis.append(date+" "+time)
	return listXAxis

# 多个文件的X轴
def GetTotalTime(listFile):
	intMax=0
	for strFile in listFile:
		listTime=GetXAxis_SingleFileMutilKey(strFile)
		start=datetime.datetime.strptime(listTime[0],"%d-%b-%Y %H:%M:%S")
		end=datetime.datetime.strptime(listTime[len(listTime)-1],"%d-%b-%Y %H:%M:%S")
		intTime=(end-start).days*24*60*60+(end-start).seconds
		if intTime>intMax:
			intMax=intTime
	return intMax

# 单个或多个文件的Y轴
def GetYAxis(listData,intEnd,intStep):
	listTemp=[]
	for data in listData:
		listTemp.append(min(data["data"]))
		listTemp.append(max(data["data"]))
	fMin=min(listTemp)
	fMax=max(listTemp)

	for i in range(intEnd,0-intStep,-intStep):
		if fMin>=i:
			fMin=i
			break
	for i in range(0,intEnd+intStep,intStep):
		if fMax<=i:
			fMax=i
			break
	listYAxis=range(int(fMin),int(fMax)+intStep,intStep)
	return listYAxis

def GetCPUCount(strFile):
	listData=FindDataByRegex(strFile,r'AAA,cpus,(.*)\n')
	return string.atoi(listData[0])

def GetTimePeriod(strFile):
	listData=FindDataByRegex(strFile,r'-s (.*) -c')
	return string.atoi(listData[0])
##---------------------Get data of nmon file---------------------
