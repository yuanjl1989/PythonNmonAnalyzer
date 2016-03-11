#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,shutil

reload(sys)
sys.setdefaultencoding("utf-8")

myPath=sys.path[0]
parentPath=os.path.dirname(myPath)
listPath=[myPath]
for p in listPath:
    if not p in sys.path:
        sys.path.append(p)
		

from Common import *


if __name__=='__main__':
	strTestCase=sys.argv[1]
	
	dictPath={
		"Dir":parentPath,
		"Config":parentPath+"/TestCases/"+strTestCase+"/TestRunConfig.xml",
		"TestCases":parentPath+"/TestCases/"+strTestCase+"/",
		"TestRun":parentPath+"/TestRun/"}	

	dictInterface=GetConfigInterfaceData(dictPath["Config"])
	for strInterface in GetConfigInterfaceName(dictPath["Config"]):
		for dictScene in dictInterface[strInterface]:
			srcFile=dictPath["TestCases"]+strInterface+'.jmx'
			destFile=dictPath["TestRun"]+strInterface+'_thread'+dictScene["thread"]+'_loop'+dictScene["loop"]+'.jmx'
			shutil.copy(srcFile,destFile)
			SetXmlElement_Text(destFile,'.//ThreadGroup//*[@name="ThreadGroup.num_threads"]',dictScene["thread"])
			SetXmlElement_Text(destFile,'.//ThreadGroup//*[@name="LoopController.loops"]',dictScene["loop"])