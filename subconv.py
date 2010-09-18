#!/usr/bin/python

#Author:  Lukasz Osipiuk  & Paulina "Ofieczka" Kania
#Licence: GNU GPL
#Name:    subconv - Subtitles Converting/Edititng Tool 

lineend = '\n'
separator = '|'
stringquote = '"'
stringquote = "\""
replacequote = "`"
lastingMode = "nomode"
lastingTime = 3000
minLastingTime = 0
maxLastingTime = 60000*10 #10 minutes
doLastingTime = 0
doNoDeaf = None
doRemoveRegExp = None
doSmartScale = None
regexp = None
framerate = 23.98
scale = None
splits = None
getSplit = None
splitsep = "====="
shift = 0


dividers = [60*60*1000, 60*1000, 1000 ,1]

from sys import stdin, argv, stderr, stdout, exit
import string
import re
import getopt


# Exceptions definitions

class SubconvError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return `self.msg`
    def message(self):
        return self.msg

class InternalSubconvError(SubconvError):
    pass


#Error notification
def PrintFormatError(format, linenum, line):
    stderr.write("Error in input data (" + format + "). Line " + str(linenum) +": '" + line + "'\n")


def ReadRawLines(input = stdin):
    lines = input.readlines()
    lines = map(string.rstrip, lines)
    return lines


def intround(f):
    return int(round(f))

def Ms2Time(ms):
    global dividers
    
    ret = [0,0,0,0]
    for i in range(4):
        ret[i] = ms/dividers[i]
        ms = ms%dividers[i]
    return ret

def Time2Ms(time):
    global dividers

    ret = 0 
    for i in range(4):
        ret = ret + time[i]*dividers[i]
    return intround(ret)


def WithZero(number, howMuch):  #howMuch must be >= number lenght
    result = ""
    for i in range(howMuch - len(str(number))):
        result = result + "0"
    return result + str(number)


def StrLenNoWhiteSpaces(str):
    length = 0
    for i in str:
        if not (i in string.whitespace):
            length = length + 1
    return length

#count lasting time for one subtitle
#it cares about minimal & maximal subs time
def countLastingTime(sub, nextStartTime):
    global lastingTime;

    startTime = sub[0]
    endTime = sub[1]
    line = sub[2]
    newTime = 0

    # if bad data in input format we try to repair it
    if (startTime > nextStartTime):
        nextStartTime = startTime + maxLastingTime
        
    #we use temporary variable in case of "nomode"
    tmpLastingTime = lastingTime

    # multiplier of lastingTime (number of words, chars etc)
    length = 0

    if lastingMode == "line":
        length = len(line)
    elif lastingMode == "subtit":
        length = 1           
    elif lastingMode == "word":
        for j in line:
            length = length + len(string.split(j))
    elif lastingMode == "char":
        for j in line:
            length = length + StrLenNoWhiteSpaces(j)
    elif lastingMode == "nomode":
        #just handle min and maxlastingtime
        length = 1
        tmpLastingTime = endTime - startTime
    else:
        raise InternalSubconvError("Bad subtitle lasting mode.")

    # sub can't be longer than:
    newTime = min(startTime + length * tmpLastingTime, nextStartTime-1, startTime + maxLastingTime)

    #if new time is too short (i mean, minimal time is longer)
    if newTime < startTime + minLastingTime:
        #we must compute if min time suits here - if not we take the longest time matching
        minTime = min(startTime + minLastingTime, nextStartTime-1, startTime + maxLastingTime)
        #if new time was longer than min don't do anything
        if minTime > newTime:                    
           newTime = minTime
        
    return newTime
#end countLastingTime

def countLastingTimeForAllSubs(subs):
    #guard
    timeGuard = 999999999

    tline = []
    tline.append(timeGuard)
    tline.append(0)
    subs.append(tline) 

    #we count lasting time for all lines
    for i in range(len(subs)-1): 
        subs[i][1] = countLastingTime(subs[i], subs[i+1][0])

    #remove guard
    del subs[len(subs)-1]
    return subs
#end countLastingTimeForAllSubs

####### From... functions convert from given format to list
####### [start, end, ["line1", "line2", ... , "linen"]]
####### start and end are in miliseconds        

def FromCSV(rawlines):
    reobject = re.compile("^(?P<d1>\d+)(?P<sep>[,;\t])(?P<d2>\d+)(?P=sep)"+
                          "(?:(?P<ciapek>[\"'#`])(?P<n1>.*)(?P=ciapek)|(?P<n2>.*))")
    lines = []
    counter = 0
    for line in rawlines:
        counter = counter + 1
        searchob = reobject.search(line)
        if searchob:
            newsub = []
            newsub.append(int(searchob.group("d1")))
            newsub.append(int(searchob.group("d2")))
            if searchob.group("n1"):
                napisy = searchob.group("n1") #napisy w ciapkach
            elif searchob.group("n2"):
                napisy = searchob.group("n2") #napisy bez ciapkiw
            else:
                napisy = ""
                
            newsub.append(string.split(napisy, '|'))
            lines.append(newsub)
        else:
            PrintFormatError("CSV", counter, line)
    return lines
#end FromCSV


def FromMicroDVD(rawlines):
    global framerate
    
    reobject = re.compile("^{(\d+)}{(\d+)}(.*)")
    lines = []
    counter = 0
    for line in rawlines:
        counter = counter + 1
        searchob = reobject.search(line)
        if searchob:
            newsub = []
            newsub.append(intround((int(searchob.group(1))*1000)/framerate))
            newsub.append(intround((int(searchob.group(2))*1000)/framerate))
            if searchob.group(3):
                newsub.append(string.split(searchob.group(3), '|'))
            else:
                newsub.append("")
            lines.append(newsub)
        else:
            PrintFormatError("microdvd", counter, line)
    return lines
#end FromMicroDVD


def FromSubRip(rawlines):
    reobject = re.compile("^(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)")
    renumline = re.compile("^\d+$")
    temp = []
    elem = []
    lines = []
    skipnext = 1
    timesearchnext = 0
    work = 0
    for i in range(0, len(rawlines)):
        if skipnext:
            search = renumline.match(rawlines[i])
            if search:
                skipnext = 0
                timesearchnext = 1
            else:
                if (rawlines[i] != ''):
                    # something different than single number or newline
                    PrintFormatError("SubRip", i+1, rawlines[i])
        elif rawlines[i] == '':
            if work:
                elem.append(lines)
                temp.append(elem)
                elem = []
                lines = []
                work = 0
                skipnext = 1
        elif timesearchnext:
            search = reobject.match(rawlines[i])
            if search: #rozpoczynamy nowy blok
                work = 1
                elem.append(Time2Ms((int(search.group(1)),
                                     int(search.group(2)),
                                     int(search.group(3)),
                                     int(search.group(4)))))
                elem.append(Time2Ms((int(search.group(5)),
                                     int(search.group(6)),
                                     int(search.group(7)),
                                     int(search.group(8)))))
                timesearchnext = 0
            else:
                # no timestamp where it should be
                PrintFormatError("SubRip", i+1, rawlines[i])
            
        else:            
            if work:
                lines.append(rawlines[i])
            else:
                PrintFormatError("SubRip", i+1, rawlines[i])
    if work:
        elem.append(lines)
        temp.append(elem)

    return temp
# end FromSubRip

def FromSubviewer(rawlines):
    reheader = re.compile("^\[.*")    
    reobject = re.compile("^(\d+):(\d+):(\d+).(\d+),(\d+):(\d+):(\d+).(\d+)")
    temp = []
    elem = []
    lines = []
    work = 0

    j = 0
    while reheader.search(rawlines[j]):
        j = j + 1

    for i in range(j, len(rawlines)):
        if rawlines[i] == '':
            if work:
                elem.append(lines)
                temp.append(elem)
                elem = []
                lines = []
                work = 0
        else:
            search = reobject.search(rawlines[i])
            if search: #rozpoczynamy nowy blok
                work = 1
                elem.append(Time2Ms((int(search.group(1)),
                                     int(search.group(2)),
                                     int(search.group(3)),
                                     int(search.group(4)) * 10)))
                elem.append(Time2Ms((int(search.group(5)),
                                     int(search.group(6)),
                                     int(search.group(7)),
                                     int(search.group(8)) * 10)))
            elif work: #dzielimy na linie...
                ak = string.split(rawlines[i],'[br]')
                for k in ak:
                    lines.append(k)                    
            else:
                PrintFormatError("SubViewer", i, rawlines[i])

    if work:#jesli koniec pliku a my nie dodalismy jeszcze wszystkich napisow
        elem.append(lines)
        temp.append(elem)

    return temp
# end FromSubviewer



def FromTMPlayer(rawlines):
    global lastingMode

    reobject = re.compile("^(\d+):(\d+):(\d+):(.*)")
    temp = []
    counter = 0
    for line in rawlines:
        counter = counter + 1
        searchob = reobject.search(line)
        if searchob:
            tline = []
            tline.append(Time2Ms((int(searchob.group(1)),
                                  int(searchob.group(2)),
                                  int(searchob.group(3)),
                                  0)))
            tline.append(0)
            if searchob.group(4):
                tline.append(string.split(searchob.group(4), '|'))
            else:
                tline.append("")
                
            temp.append(tline)
        else:
            PrintFormatError("TMPlayer", counter, line)
            
    #if we have 00:00:00 in last line we remove it
    if temp[-1][0] == 0:
        del temp[-1]
            
    #If user didnt specified any mode we use /s
    if (lastingMode == "nomode"):
        lastingMode = "subtit"
    
    return temp  
#end FromTMPlayer

def FromJacosub(rawlines):
    reheader = re.compile("^#.*")
    reobject = re.compile("^(\d+):(\d+):(\d+).(\d+)\s*(\d+):(\d+):(\d+).(\d+)\s*\S*\s*(.+)")
    lines = []
    counter = 0
    for line in rawlines:
        searchob = reheader.match(line)
        if searchob:
            pass
        else:
            searchob = reobject.match(line)
            if searchob:
                elem = []
                elem.append(Time2Ms((int(searchob.group(1)),
                                     int(searchob.group(2)),
                                     int(searchob.group(3)),
                                     int(searchob.group(4)) * 10)))
                elem.append(Time2Ms((int(searchob.group(5)),
                                     int(searchob.group(6)),
                                     int(searchob.group(7)),
                                     int(searchob.group(8)) * 10)))
                elem.append(string.split(searchob.group(9), '\\n'))
                lines.append(elem);
            else:
                PrintFormatError("Jacosub", counter, rawlines[counter])
        
        counter = counter+1
        
    return lines
#end FromJacosub



def From(rawlines, format):
    if format == "csv":
        return FromCSV(rawlines)
    elif format == "microdvd":
        return FromMicroDVD(rawlines)
    elif format == "tmplayer":
        return FromTMPlayer(rawlines)
    elif format == "subrip":
        return FromSubRip(rawlines)
    elif format == "subviewer":
        return FromSubviewer(rawlines)
    elif format == "jacosub":
        return FromJacosub(rawlines)
    raise SubconvError("Format unknown: " + format)
#end From


####### To... functions take the formated list [start, end, [...]]
####### and write subtitles in specific format to given file


#wraper which decides if we should write lines or split it first.
def To(lines, format, file):
    global lineend, splitsep

    if splits != None:
        if getSplit != None:
            _To(GetSplit(lines, splits, getSplit), format, file)
        else:
            i = 0
            for l in Split(lines, splits):
                i = i + 1
                _To(l, format, file)
                if i <= len(splits):
                    file.write(lineend + splitsep + lineend)
    else:
        _To(lines, format, file)
        
  
#writes lines to file in specific format.
def _To(lines, format, file):
    if format == "csv":
        return ToCSV(lines, file)
    elif format == "microdvd":
        return ToMicroDVD(lines, file)
    elif format == "tmplayer":
        return ToTMPlayer(lines, file)
    elif format == "subrip":
        return ToSubRip(lines, file)
    elif format == "subviewer":
        return ToSubviewer(lines, file)
    elif format == "jacosub":
        return ToJacosub(lines, file)
    elif format == "notime":
        return ToNoTime(lines, file)
    raise SubconvError("Format unknown: " + format)


def ToCSV(lines, output = stdout):
    global lineend, separator, stringquote, replacequote

    for line in lines:
        t = string.join(line[2],separator)
        if replacequote != "":
           #we replace all stringquote to replacequote to allow beter importing into spreadsheet eg.
           t = t.replace(stringquote, replacequote)
        output.write(str(line[0]) + ',' +
                     str(line[1]) + ',' +
                     stringquote + t + stringquote + lineend)


def ToMicroDVD(lines, output = stdout):
    global framerate, lineend, separator

    for line in lines:
        output.write("{" + str(intround((line[0])*framerate/1000.0)) + "}" +
                     "{" + str(intround((line[1])*framerate/1000.0)) + "}" +
                     string.join(line[2],separator)+lineend)


def ToSubRip(lines, output = stdout):
    global lineend

    i = 0
    for line in lines:
        i = i+1
        starttime = Ms2Time(line[0])
        endtime = Ms2Time(line[1])
        output.write(str(i)+lineend)
        output.write(WithZero(starttime[0],2) + ":" +
                     WithZero(starttime[1],2) + ":" +
                     WithZero(starttime[2],2) + "," +
                     WithZero(starttime[3],3) + " --> " +
                     WithZero(endtime[0],2)+ ":" +
                     WithZero(endtime[1],2) + ":" +
                     WithZero(endtime[2],2) + "," +
                     WithZero(endtime[3],3) + lineend)
        for l in line[2]:
            output.write(l+lineend)
        output.write(lineend)
#end TOSubRip

def ToSubviewer(lines, output = stdout):
    global lineend
    output.write("[INFORMATION]" + lineend +
                 "[AUTHOR]" + lineend +
                 "[SOURCE]" + lineend +
                 "[PRG]" + lineend +
                 "[FILEPATH]" + lineend +
                 "[DELAY]" + lineend +
                 "[CD TRACK]" + lineend +
                 "[COMMENT]" + lineend +
                 "[END INFORMATION]" + lineend +
                 "[SUBTITLE]" + lineend +
                 "[COLF]&HFFFFFF,[STYLE]no,[SIZE]18,[FONT]Arial" + lineend)
    
    for line in lines:
        starttime = Ms2Time(line[0])
        endtime = Ms2Time(line[1])
        output.write(WithZero(starttime[0],2) + ":" +
                     WithZero(starttime[1],2) + ":" +
                     WithZero(starttime[2],2) + "." +
                     WithZero(int(starttime[3]/10),2) + "," +
                     WithZero(endtime[0],2)+ ":" +
                     WithZero(endtime[1],2) + ":" +
                     WithZero(endtime[2],2) + "." +
                     WithZero(int(endtime[3]/10),2) + lineend)
        ak = ""
        for l in line[2]:
            ak = ak + l + "[br]"
        output.write(ak[:-4] + lineend + lineend)
#end TOSubviewer


def ToTMPlayer(lines, output = stdout):
    global lineend, separator

    for line in lines:
        starttime = Ms2Time(line[0])
        for i in range(3):
            output.write(WithZero(starttime[i], 2) + ":")
        output.write(string.join(line[2],separator)+lineend)
    output.write("00:00:00:")

#end ToTMPlayer

def ToJacosub(lines, output = stdout):
    global lineend, separator

    for line in lines:
        starttime = Ms2Time(line[0])
        endtime = Ms2Time(line[1])
        output.write(WithZero(starttime[0], 2) + ":")
        output.write(WithZero(starttime[1], 2) + ":")
        output.write(WithZero(starttime[2], 2) + ".")
        output.write(WithZero(starttime[3]/10, 2) + " ")
        output.write(WithZero(endtime[0], 2) + ":")
        output.write(WithZero(endtime[1], 2) + ":")
        output.write(WithZero(endtime[2], 2) + ".")
        output.write(WithZero(endtime[3]/10, 2) + " JC ")
        output.write(string.join(line[2],'\\n')+lineend)

#end ToTMPlayer


def ToNoTime(lines, output = stdout):
    global lineend, separator

    for line in lines:
        output.write(string.join(line[2],separator)+lineend)
#end ToNoTime


# Tries to guess the format of data based on lines read from file
def GuessFormat(rawlines):
    if (len(rawlines) == 0): #nie ma nic do roboty
        raise SubconvError("Could not guess input subtitles format")
    
    subTypes = [["microdvd", "^{\d+}{\d+}.*"],
                ["tmplayer", "^\d+:\d+:\d+:.*"],
                ["subrip", "^\d+$"],
                ["csv", "^\d+(?P<sep>[,;\t])\d+(?P=sep)(?:(?P<ciapek>[\"#'`])(?:.+)(?P=ciapek)|(?:.+))"],
                ["subviewer", "^\[INFORMATION\]"]]
    subLen = len(subTypes)
    for i in range(subLen):
        reobject = re.compile(subTypes[i][1])
        line = rawlines[0]
        searchob = reobject.match(line)
        if searchob:
            return subTypes[i][0]

    raise SubconvError("Could not guess input subtitles format")

#end GuessFormat


# Shifts subtitles by given time (in ms)
def Shift(lines, value):
    #we do not shift if value is 0
    if not value:
        return lines
    
    t = []
    if value:
        for i in lines:
            # przesuwamy czas o wartosc zadana
            i[0] = i[0] + value
            if i[0] < 0:
                i[0] = 0

            i[1] = i[1] + value
            if i[1] < 0:
                i[1] = 0
                    
            t.append(i)
    else:
        t = lines

    return t    
#end Shift

#Scales subtitles by given float value
def Scale(lines, value):
    t = []
    for i in lines:
        # we scale time by given value
        i[0] = intround(i[0] * value)
        i[1] = intround(i[1] * value)
            
        t.append(i)

    return t    
#end Scale



#returns n-th split piece
def GetSplit(lines, splits, num):
    if (num > len(splits)+1) or (num <= 0):
        raise SubconvError("To big or to small piece number requested.")

    l2 = lines
    if num > 1:
        (l1, l2) = DoSplit(lines, splits[num-2]);

    if num <= len(splits):
        #we should split l2
        (l2 , l1) = DoSplit(l2, splits[num-1])

    #we have to shift our piece a bit
    if num > 1:
        Shift(l2, -splits[num - 2])
        
    return l2                            
    

# Splits subititles into two parts at value.
# Tuple of two lists is returned
def DoSplit(lines, value):
    r = len(lines) - 1
    l = 0
    
    #we find the place to cut the list
    while  r >= l:
        med = (l+r)/2
        if lines[med][0] < value:
            l = med+1
        else:
            r = med-1

    #we should cut [l:r-1],[r:length(lines)]
    l1 = lines[0:r+1]
    l2 = lines[r+1:len(lines)]

    # we shift the second list
    # l2 = Shift(l2, -value)
    return (l1, l2)

# splits a list of subtitles into list of lists at given timestamps.
def Split(lines, splits):

    t = lines
    ret = []
    lastsplit = 0;
    for split in splits:
        (h,t) = DoSplit(t, split)
        ret.append(Shift(h, -lastsplit))
        lastsplit = split

    ret.append(Shift(t, -lastsplit))
    
    return ret


###### Removes from subtitles part od subs intended for deaf people
###### in format "[...]"
def RemoveDeafSubs(lines):
    return RemoveRegExp(lines, "\[.*?\]")


###### Removes from one subtitle part of lines matching given regular
###### expression
def RemoveRegExpInOneSub(lines, reobject):
    t = []    
    for line in lines:
        newline = re.sub(reobject, "", line)
        if newline != "":
            t.append(newline)
    return t

###### Removes from subtitles part of subs matching given regular
###### expression
def RemoveRegExp(lines, regexp):

    # we remove either pattern + space if we are inside the line
    # or only pattern in the end of line
    reobject = re.compile(regexp + " |" + regexp)
    
    ret = []
    for sub in lines:
        line = RemoveRegExpInOneSub(sub[2], reobject)
        if line != []:
            newSub = []
            newSub.append(sub[0])
            newSub.append(sub[1])
            newSub.append(line)
            ret.append(newSub)            
    return ret

def SmartScale(lines, first, last):
    firstSub = lines[0][0]
    lastSub  = lines[-1][0]

    scale = float((last - first)) / float((lastSub - firstSub))
    shift = intround(first - scale * firstSub)

    return (scale, shift)


####### Converts string in HHhMMmSSsMS format to list format 
####### It returns list and sign               
def Str2TimeList(timeString):
    time = [0, 0, 0, 0]
    sign = 1  #znak +

    if timeString[0] == '-':  # jesli podany czas jest ujemny
        sign = -1;
        timeString = timeString[1:]

    reobject = re.compile("^(?P<h>(\d+\.\d+h)|(\d+h))?" +
                           "(?P<m>(\d+\.\d+m)|(\d+m))?" +
                           "(?P<s>(\d+\.\d+s)|(\d+s))?" +
                           "(?P<ms>\d+)?$|"             +
                           "^(?P<f>(\d+\.\d+f)|(\d+f))$") #przesuniecie w ramkach
    searchob = reobject.match(timeString)
    if searchob:
        ak = searchob.group("f") #jesli przesuniecie w ramkach
        if ak:
            time[3] = float(ak[:-1]) * 1000.0 / framerate
        else: #przesuniecie w formacie hms
            j = 0
            for i in ["h", "m", "s", "ms"]:
                ak = searchob.group(i)
                if ak:
                    if i != "ms":  #tylko ms nie maja na koncu dodatkowej literki 
                        time[j] = float(ak[:-1])
                    else:
                        time[j] = float(ak)
                else:
                    time[j] = 0
                j = j + 1
    else:
        raise SubconvError("Time format error")

    return (time, sign)
#end Str2TimeList    


def Str2ShiftTime(timeString): 
    (list, sign) = Str2TimeList(timeString)
    time = Time2Ms(list)
    return (sign * time)

def Str2LastingTime(timeString):
    mode = "line"
    reobject = re.compile("(?P<w>.*/w$)|" +
                          "(?P<c>.*/c$)|" +
                          "(?P<l>.*/l$)|" +
                          "(?P<s>.*/s$)|" +                                                    
                          "(?P<d>\w*$)")
    searchob = reobject.match(timeString)

    if searchob:
        if searchob.group("w"):
            strTime = (searchob.group("w"))[:-2]
            mode = "word"
        elif searchob.group("c"):
            strTime = (searchob.group("c"))[:-2]
            mode = "char"
        elif searchob.group("l"):
            strTime = (searchob.group("l"))[:-2]
            mode = "line"
        elif searchob.group("s"):
            strTime = (searchob.group("s"))[:-2]
            mode = "subtit"
        elif searchob.group("d"):
            strTime = (searchob.group("d"))
            mode = "subtit"
    else:        
        raise SubconvError("Lasting time format error")

    (timeList, sign) = Str2TimeList(strTime)
    time = Time2Ms(timeList)

    #we do not accept values below zero
    if sign == -1:
        raise SubconvError("Lasting time format error")

    return (time, mode)

def PrintMiniHelp():
    stderr.write("""Use subconv.py -h for help

""")

def PrintHelp():
    stdout.write("""
Usage: subconvert.py [-i fromfile] [-o tofile]
                     [-r informat] [-w outformat] [-l lastingtime]
                     [-f framerate] [-s timeshift]
                     [-c scale] [-p split1,split2,...]
                     [other_forgotten_switches ;)] [-h]


By default program reads data from stdin and writes to stdout.

Switches:

 -i --inputfile    Assigns a filename to read data from. (default is stdin)
 -o --outputfile   Assigns a filename to write data to. (default is stdout)
 -r --inputformat  Forces input format (normally program does auto-detection)
 -w --outputformat Selects output format (default is csv)
 -f --framerate    Set the framerate for reading/writing in MicroDVD format 
                   (default is 23.98 fps).
 -s --shift        Shifts subtitles by given value (in special time format)
 -c --scale        Multiplies time of subtitles by given float value
    --smartscale   Takes two comma separated parameters : starting time of first
                   and last subtitle and basing on them adjusts all subtitles 
 -p --split        Splits subtitles at given place (in special time format)
                   If you want the file to be splitted into several pieces
                   pass a comma separated list of timestamps.
    --splitsep     Sets the separator to put between splited parts of
                   subtitles in output file (default is \"=====\")
    --getsplit <n> Outputs just n-th part (without separators).
                   Counted from 1.
 -l --lasttime     Sets how long should last a subtitle (when reading data in
                   format without such info eg. TMPlayer) (default is 3000ms)
                   Following formats are possible:
                     1) time      - refers to subtitle
                     2) time/c    - refers to character
                     3) time/l    - refers to line
                     4) time/s    - refers to subtitle
                     5) time/w    - refers to word
     --mintime     Sets minimal subtitle's lasting time
     --maxtime     Sets maximal subtitle's lasting time
     --nodeaf      Removes parts of subtitles intended for deaf people
                   (this means various sounds from environment).
     --delregexp   Removes parts of subtitles matching given regular expression.
                   Warning: this works only on separated lines not on all subtitle.
 -h --help         Shows this info
 -?                Shows this info

Supported formats:
   csv       - Comma separated values (semicolon for real :)).
               All \" in text are replaced with ` to allow nice importing
               (eg. to spreadsheet program).
   microdvd  - Format based on frames. Uses given framerate (default is 23.98)
   subrip    - hh.mm.ss,mmm -> hh.mm.ss,mmm format
   tmplayer  - hh:mm:ss format
   notime    - Just subtitles without time info at all (subformat like in microdvd).
               Only write in this format is supported
   subviewer - Header + hh:mm:ss.xx,hh:mm:ss.xx format, where xx means 10*ms
   jacosub   - Some kinda shi...  - #params and then hh:mm:ss.xx hh:mm:ss.xx JC sub
   
Time format:
   [-][HHh][MMm][SSs][MS] - HH, MM, SS stand for any float value and MS is integer.
or [-][FFf]               - FF is a float value. f refers to frames.

eg. -1h10.5s10 - means minus one hour, 10 and half seconds and 10 miliseconds.

""")
    
######### MAIN PROGRAM #############

def main():
    global lineend, separator, stringquote, replacequote, lastingMode
    global minLastingTime, maxLastingTime, lastingTime, framerate, scale, getSplit, splitsep, splits
    global doLastingTime, shift, doNoDeaf, doRemoveRegExp, regexp, doSmartScale, startTime, endTime

    inputfile = stdin
    outputfile = stdout
    inputformat = ""
    outputformat = ""

    
    try:
        opts, args = getopt.getopt(argv[1:], "i:o:r:w:f:l:h?s:c:p:",
                                   ["inputfile=", "outputfile=",
                                    "inputformat=", "outputformat=",                                    
                                    "lasttime=", "mintime=", "maxtime=",
                                    "split=", "splitsep=", "getsplit=",
                                    "shift=", "scale=", "smartscale=",
                                    "nodeaf", "delregexp=", "help"])
    except getopt.GetoptError:
        stderr.write("\nError in arguments!\n")
        PrintMiniHelp()
        exit(1)


    try:
        for o, a in opts:
            if o in ("-h", "-?", "--help"):
                PrintHelp()
                exit(0);
            if o in ("-i", "--inputfile"):
                try:
                    inputfile = file(a, "r")
                except IOError:
                    stderr.write("Cant open input file.\n")
                    exit(1)
            elif o in ("-o", "--outputfile"):
                try:
                    outputfile = file(a, "w")
                except IOError:
                    stderr.write("Cant open output file.\n")
                    exit(1)
            elif o in("-r", "--inputformat"):
                inputformat = a
            elif o in ("-w", "--outputformat"):
                outputformat = a
            elif o in ("-f", "--framerate"):
                framerate = float(a)
            elif o in ("-s", "--shift"):
                shift = Str2ShiftTime(a)
            elif o in ("-l", "--lasttime"):
                (lastingTime, lastingMode) = Str2LastingTime(a)
            elif o == "--mintime":
                doLastingTime = 1
                minLastingTime = Str2ShiftTime(a)
                if minLastingTime < 0:
                    raise SubconvError("Time format error in --mintime")
            elif o == "--maxtime":
                doLastingTime = 1
                maxLastingTime = Str2ShiftTime(a)
                if maxLastingTime < 0:
                    raise SubconvError("Time format error in --maxtime")
            elif o in ("-c", "--scale"):
                try:
                    scale = float(a)
                except ValueError:
                    raise SubconvError("--scale should get float argument\n");
            elif o in ("-p", "--split"):
                splitTmp = string.split(a, ',')
                splits = []
                for s in splitTmp:
                    splits.append(Str2ShiftTime(s))
                splits.sort()
            elif o == "--splitsep":
                splitsep = a
            elif o == "--getsplit":
                try:
                    getSplit = int(a)
                except ValueError:
                    raise SubconvError("--getSplit should get integer argument\n");
            elif o == "--nodeaf":
                doNoDeaf = 1
            elif o == "--delregexp":
                doRemoveRegExp = 1
                regexp = a
            elif o == "--smartscale":
                doSmartScale = 1
                timeValues = []
                for t in string.split(a, ','):
                    timeValues.append(Str2ShiftTime(t))

                if len(timeValues) != 2:
                    raise SubconvError("You must specify time value of first and last subtitle\n")

                timeValues.sort()
                
                startTime = timeValues[0]
                endTime   = timeValues[1]

    except SubconvError, e:               
        stderr.write(e.message()+"\n")
        PrintMiniHelp()
        exit(1)


    try:
        rawlines = ReadRawLines(inputfile)

        if inputformat == "": #zgadujemy
            inputformat = GuessFormat(rawlines)

        if outputformat == "":
            outputformat = inputformat;


        lines = From(rawlines, inputformat)

        if doNoDeaf != None:
            lines = RemoveDeafSubs(lines)

        if doRemoveRegExp != None:
            lines = RemoveRegExp(lines, regexp)

        if doSmartScale != None:
            (scale, shift) = SmartScale(lines, startTime, endTime)

        if scale != None:
            lines = Scale(lines, scale)

        if shift != 0:
            lines = Shift(lines, shift)

        if lastingMode != "nomode" or doLastingTime:
            lines = countLastingTimeForAllSubs(lines)

        To(lines, outputformat, outputfile) #OK

        if not (inputfile is stdin):
             inputfile.close()
        if not (outputfile is stdout):

             outputfile.close()

    except SubconvError, e:
        stderr.write(e.message()+"\n")
        exit(1)
         
try:
    main()
except KeyboardInterrupt:
    stderr.write("Caught SIGINT from user. Exiting. \n")
