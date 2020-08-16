# -*- coding: utf-8 -*-

"""
@author: jason
"""

import os
import hashlib

def getListFromFile(filepath):
    """
    Get list from filepath.
    """
    alist = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        linelist = f.readlines()
        for line in linelist:
            lineStrip = line.strip()
            if len(lineStrip) == 0:
                continue
            flag = lineStrip.startswith('#')
            if flag == True:
                continue
            alist.append(lineStrip)
    return alist

def getInfoDict(filepath, exeName=''):
    """
    Get dict{'key':dict} from filepath
    """
    aDict = {}
    head = ''
    executeName = ''
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        linelist = f.readlines()
        for line in linelist:
            lineStrip = line.strip()
            if len(lineStrip) == 0:
                continue
            flag = lineStrip.startswith('#')
            if flag == True:
                continue
            flag = lineStrip.startswith('EXECUTE_NAME')
            if flag == True:
                index = lineStrip.find('=')
                executeName = lineStrip[index+1:]
                continue
            flag = lineStrip.startswith('[')
            if flag == True:
                flag2 = lineStrip.endswith(']')
                if flag2 == True:
                    index1 = lineStrip.find('[')
                    index2 = lineStrip.find(']')
                    head = lineStrip[index1+1:index2]
                    value = {}
                    aDict[head] = value
                else:
                    continue
            else:
                if head == '':
                    continue
                indexNum = lineStrip.find('=')
                if indexNum != -1:
                    secDict = aDict.get(head)
                    key = lineStrip[0:indexNum]
                    value = lineStrip[indexNum+1:]
                    secDict[key] = value
                    aDict[head] = secDict
                else:
                    continue
    
    tarDict = {}
    if exeName == '':
        tarDict = aDict.get(executeName)
    else:
        tarDict = aDict.get(exeName)
        if tarDict == None:
            tarDict = {}
    return tarDict

def getDictFromFile(filepath, splitStr='='):
    """
    Get dict from filepath.
    Read lines from file with filepath, and each line uses parameter splitStr
    to split itself to a dict. One line is an element of dict.
    Example as below:
    
    a1=Mon,Tue,Wed,Thu
    a1=Fri
    a2=Tue
    a3=Wed
    ...
    ...
    ...
    
    convert to {'a1':'Mon,Tue,Wed,Thu,Fri','a2':'Tue','a3':'Wed', ...}
    
    """
    aDict = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        linelist = f.readlines()
        for line in linelist:
            lineStrip = line.strip()
            if len(lineStrip) == 0:
                continue
            flag = lineStrip.startswith('#')
            if flag == True:
                continue
            indexNum = lineStrip.find(splitStr)
            if indexNum != -1:
                key = lineStrip[0:indexNum]
                value = lineStrip[indexNum+1:]
                if aDict.get(key) == None:
                    aDict[key] = value
                else:
                    tmpValue = aDict.get(key)
                    if tmpValue[len(tmpValue)-1:] == ',':
                        tmpValue = tmpValue + value
                    else:
                        tmpValue = tmpValue + ',' + value
                    aDict[key] = tmpValue
            else:
                continue
    return aDict

def getDictOfDict(filepath):
    """
    Get dict{'key':dict} from filepath
    """
    targetDict = {}
    head = ''
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        linelist = f.readlines()
        for line in linelist:
            lineStrip = line.strip()
            if len(lineStrip) == 0:
                continue
            flag = lineStrip.startswith('#')
            if flag == True:
                continue
            flag = lineStrip.startswith('[')
            if flag == True:
                flag2 = lineStrip.endswith(']')
                if flag2 == True:
                    index1 = lineStrip.find('[')
                    index2 = lineStrip.find(']')
                    head = lineStrip[index1+1:index2]
                    value = {}
                    targetDict[head] = value
                else:
                    continue
            else:
                if head == '':
                    continue
                indexNum = lineStrip.find('=')
                if indexNum != -1:
                    secDict = targetDict.get(head)
                    key = lineStrip[0:indexNum]
                    value = lineStrip[indexNum+1:]
                    secDict[key] = value
                    targetDict[head] = secDict
                else:
                    continue
    
    return targetDict

def formatDate(dateStr):
    """
    format dateStr(yyyyMMdd) to yyyy/MM/dd
    """
    if len(dateStr) < 8:
        return dateStr
    dateInt = int(dateStr)

    yearInt = int(dateInt / 10000)
    monthInt = int(dateInt % 10000 / 100)
    ddInt = dateInt % 100

    tarStr = str(yearInt)
    tarStr += '/'
    if monthInt < 10:
        tarStr += '0'
    tarStr += str(monthInt)
    tarStr += '/'
    if ddInt < 10:
        tarStr += '0'
    tarStr += str(ddInt)
    
    return tarStr

def formatTime(timeStr):
    """
    format timeStr(HHmmsssss) to HH:mm:ss.sss
    format timeStr(HHmmss) to HH:mm:ss
    format timeStr(HHmm) to HH:mm
    """
    timeLen = len(timeStr)
    if timeLen < 3:
        return timeStr
    
    tarStr = ""
    timeInt = int(timeStr)
    if timeLen == 3 or timeLen == 4:
        hh = int(timeInt / 100)
        mm = int(timeInt % 100)
        if hh < 10:
            tarStr += "0"
        tarStr += str(hh)
        tarStr += ':'
        if mm < 10:
            tarStr += '0'
        tarStr += str(mm)        
        return tarStr
    elif timeLen == 5 or timeLen == 6:    
        hh = int(timeInt / 10000)
        mm = int(timeInt % 10000 / 100)
        ss = int(timeInt % 100)
        if hh < 10:
            tarStr += "0"
        tarStr += str(hh)
        tarStr += ':'
        if mm < 10:
            tarStr += '0'
        tarStr += str(mm)
        tarStr += ':'
        if ss < 10:
            tarStr += '0'
        tarStr += str(ss)        
        return tarStr

    hh = int(timeInt / 10000000)
    mm = int(timeInt % 10000000 / 100000)
    ss = int(timeInt % 100000 / 1000)
    sss = int(timeInt % 1000)

    if hh < 10:
        tarStr += "0"
    tarStr += str(hh)
    tarStr += ':'
    if mm < 10:
        tarStr += '0'
    tarStr += str(mm)
    tarStr += ':'
    if ss < 10:
        tarStr += '0'
    tarStr += str(ss)
    tarStr += "."
    if sss < 10:
        tarStr += "00"
    elif sss < 100:
        tarStr += "0"
    tarStr += str(sss)
    
    return tarStr

def formatDateTime(dateTimeStr):
    """
    日期時間格式如下所示:
    1.HHmm: 返回HH:mm
    2.HHmmss: 返回HH:mm:ss
    3.yyyyMMdd: 返回yyyy/MM/dd
    4.HHmmsssss: 返回HH:mm:ss.sss
    5.yyyyMMddHHmm: 返回yyyy/MM/dd HH:mm
    """
    if len(dateTimeStr) <= 6:
        return formatTime(dateTimeStr)
    elif len(dateTimeStr) <= 8:
        return formatDate(dateTimeStr)
    elif len(dateTimeStr) <= 9:
        return formatTime(dateTimeStr)
    else:
        dateStr = dateTimeStr[0:8]
        timeStr = dateTimeStr[8:]
        return formatDate(dateStr) + " " + formatTime(timeStr)    
    
def calcTimeNum(startTime, endTime):
    if startTime > endTime:
        return 0
    aNum = 0
    aRoundNum = None
    for aTime in range(int(startTime), int(endTime) + 1):
        aRoundNum = aTime % 100
        if aRoundNum <= 59:
            aNum += 1
    return aNum            
    
def getMd5Pwd(password):
    pwdencode = password.encode('utf-8')
    return hashlib.md5(pwdencode).hexdigest()

def checkBacktestDir():
    userConf = getDictFromFile(os.path.join(os.path.dirname(__file__), "../conf/user.ini"))
    bk_select_dir = userConf.get("BACKTEST_SELECT_DIR")
    bk_file_dir = userConf.get("BACKTEST_DIR")
    if bk_select_dir == None or bk_select_dir == None:
        bk_select_dir = os.path.join(os.path.dirname(__file__), "../")
        bk_file_dir = os.path.join(os.path.dirname(__file__), "../data")
    else:
        if not os.path.exists(os.path.abspath(bk_select_dir)):
            bk_select_dir = os.path.join(os.path.dirname(__file__), "../")
            bk_file_dir = os.path.join(os.path.dirname(__file__), "../data")
    if not os.path.exists(os.path.abspath(bk_select_dir)):
        os.mkdir(os.path.abspath(bk_select_dir))
        os.mkdir(os.path.abspath(bk_file_dir))
    else:
        if not os.path.exists(os.path.abspath(bk_file_dir)):
            os.mkdir(os.path.abspath(bk_file_dir))
    
    return bk_select_dir, bk_file_dir

if __name__ == '__main__':
    print(formatDate("20181101"))
    print(formatTime("90103586"))
    print(formatTime("100110009"))
    print(calcTimeNum(900, 1330))
    #print(getMd5Pwd('135246'))
    #print(getMd5Pwd('123456'))