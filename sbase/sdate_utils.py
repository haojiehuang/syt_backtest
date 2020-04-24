# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 15:30:10 2018

@author: jason
"""

import time

def isLeapYear(aYear):
    isLeap = False
    if (aYear % 400) == 0:
        isLeap = True
    elif (aYear % 100) == 0:
        isLeap = False
    elif (aYear % 4) == 0:
        isLeap = True
    return isLeap

def getMonthDays(aYear):
    daysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isLeapYear(aYear):
        daysList[1] = 29
    return daysList

def calcDays(aYear, begMD, endMD):
    begM = int(begMD / 100)
    begD = int(begMD % 100)
    endM = int(endMD / 100)
    endD = int(endMD % 100)
    days = 0
    daysList = getMonthDays(aYear)
    if begM == endM:
        days += endD - begD + 1
    else:
        days += daysList[begM-1] - begD + 1
        for i in range(begM+1, endM):
            days += daysList[i-1]
        days += endD
    return days

def diffDays(begDate, endDate):
    if begDate > endDate:
        begYMD = endDate
        endYMD = begDate
    else:
        begYMD = begDate
        endYMD = endDate
    begYear = int(begYMD / 10000)
    begMD = int(begYMD % 10000)
    endYear = int(endYMD / 10000)
    endMD = int(endYMD % 10000)
    days = 0
    if begYear == endYear:
        days += calcDays(begYear, begMD, endMD)
    else:
        days += calcDays(begYear, begMD, 1231)
        for i in range(begYear+1, endYear):
            if isLeapYear(i):
                days += 366
            else:
                days += 365
        days += calcDays(endYear, 101, endMD)
        
    return days

def calcSeconds(srcDate, srcTime):
    """
    Parameter srcDate must >= 19700101, format is yyyyMMdd
    Parameter srcTime format is HHmmss
    """
    if srcDate < 19700101:
        return 0
    year = int(srcDate / 10000)
    month = int(srcDate % 10000 / 100)
    day = int(srcDate % 100)
    seconds = 0
    if year > 1970:        
        for yyyy in range(1970, year):
            if isLeapYear(yyyy):
                seconds += 86400 * 366
            else:
                seconds += 86400 * 365
    daysList = getMonthDays(year)
    if month > 1:
        for mm in range(1, month):
            seconds += 86400 * daysList[mm-1]
    seconds += 86400 * (day - 1)
    hour = int(srcTime / 10000)
    minute = int(srcTime % 10000 / 100)
    second = int(srcTime % 100)
    seconds += hour * 3600
    seconds += minute * 60
    seconds += second
    return seconds

def getCurrentDate():
    return int(time.strftime(format('%Y%m%d')))

def getCurrentTime():
    return int(time.strftime(format('%Y%m%d%H%M%S')))

def getPrevDate(currDate):
    year = int(currDate / 10000)
    month = int(currDate % 10000 / 100)
    day = int(currDate % 100)
    if day == 1:
        if month == 1:
            year -= 1
            month = 12
            day = 31
        else:
            month -= 1
            daysList = getMonthDays(year)
            day = daysList[month-1]
    else:
        day -= 1
    
    return year * 10000 + month * 100 + day

def getPrevTime(currDate):
    year = int(currDate / 10000)
    month = int(currDate % 10000 / 100)
    day = int(currDate % 100)
    if day == 1:
        if month == 1:
            year -= 1
            month = 12
            day = 31
        else:
            month -= 1
            daysList = getMonthDays(year)
            day = daysList[month-1]
    else:
        day -= 1
    
    hhmmss = int(time.strftime(format('%H%M%S')))
    
    return (year * 10000 + month * 100 + day) * 1000000 + hhmmss

def filteredDigit(srcTime):
    """
    return digit
    """
    if srcTime == None or srcTime == '':
        return '0'
    tarTimeStr = ''
    for i in range(len(srcTime)):
        aChar = srcTime[i]
        if aChar.isdigit():
            tarTimeStr += aChar
    
    return tarTimeStr

def transferTime(srcTime):
    """
    return yyyyMMddHHmmSS
    """
    tarTimeStr = filteredDigit(srcTime)
    if len(tarTimeStr) > 14:
        tarTimeStr = tarTimeStr[:14]
    
    return int(tarTimeStr)