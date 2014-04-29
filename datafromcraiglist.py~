#-----------------------------------
# Author : Jae Hyun Yoo
# Date   : 2014/04/27
# Description
#        : Data clustering from Craigslist
#-----------------------------------
from sys import exit
import re
import urllib2
import pprint
import operator
from bs4 import BeautifulSoup as bs
from math import sqrt

# Get datas from url ------------------------------------------
def getDataFromUrl( url ):
    loadedUrl = urllib2.urlopen( url )
    dataBuf = loadedUrl.read()
    soupObj = bs( dataBuf )
    return soupObj

# Get 2 Letters Algorithm --------------------------------------
def get2LettersFromEntry( entry ):
    entry = re.compile('[^a-z^A-Z]+').sub(' ',entry)
    listSingleWords = re.compile(' ').split( entry.strip().lower() )
    for d in ['for','a','of','get','the','with',\
                  'per','now','hiring','included',\
                  'wanted','and','you','hr','hrs','rate','to','up','are',\
                  'at','some','our','in','want','et cetera','around','your',\
                  'year old', 'yrs old', 'from','needed','need']:
        try:
            listSingleWords.remove(d)
        except:
            continue
    for l in listSingleWords:
        if len(l) == 1:
            listSingleWords.remove(l)

    listTwoWords = []
    for i in range(len(listSingleWords)-1):
        listTwoWords.append( listSingleWords[i]+' '+listSingleWords[i+1] )
    return listTwoWords

# Getting list of words from Soup Object -------------------------
def getEntriesFromSoupObj( soupObj ):
    links = soupObj( 'a' )
    listOfWordList = []
    sentinel = 0
    for i in range(len(links)):
        # print "Looking into link #%d" % i
        try:
            entry = links[i].contents[0]

            if entry.strip() == 'next >':
                sentinel += 1
                continue

            if sentinel !=  1:
                continue

            if (i%2) == 0:
                listOfWordList.append( get2LettersFromEntry( entry ) )
                # print "link #%d was sucessfull."

        except:
            # print "link #%d was not sucessful."
            continue
    return listOfWordList

# Getting subject per city (using 2 letters) -------------------------------
def getSubjectPerCity( category ):    
    subjectPerCities = []
    subjectCountPerCities = []
    for i in range(len(cities)):
        tmpLs = []
        tmpDic = {}
        subjectPerCities.append(tmpLs)
        subjectCountPerCities.append(tmpDic)
    
    subjectList = []
    for i in range(len(cities)):
        # page index
        for page in ["","100","200"]:
            url = "http://"+cities[i]+".craigslist.org/search/"+category+"/"+page+"index.html"
            soupObj = getDataFromUrl( url )
            subjectList.append(getEntriesFromSoupObj( soupObj ))
            tmp = subjectList[i]
            for j in tmp:
                for k in j:
                    subjectPerCities[i].append(k)
        for word in subjectPerCities[i]:
            subjectCountPerCities[i].setdefault(word, 0)
            subjectCountPerCities[i][word] += 1

    return subjectCountPerCities

# Sort Subjects (2 types available) ---------------------------------------
def sortData( subjects, type ):
    sortedDataPerCity = []
    evaled = {}

    for k in range(len(subjects)):
        sortedDic = sorted(subjects[k].iteritems(), key = operator.itemgetter(1), reverse = True)
        sortedDataPerCity.append(sortedDic)        
        if type == 0:
            continue

        ls = []
        for item in sortedDataPerCity[k]:
            if not ( item[1] in ls):
                ls.append(item[1])
        maxval = max(ls)
        val = {}                            
        for item in sortedDataPerCity[k]:
            val[item[0]] = float(item[1])/maxval
        evaled[cities[k]] = val
    
    if type == 0:
        return sortedDataPerCity

    return evaled

# Pearson Correlation ------------------------------------------------
def sim_pearson( m1, m2 ):
    si = []
    # find common job names
    for key in m1.keys():
        if key in m2.keys():
            si.append(key)
    n = len(si)

    # if there is no common job, return 0
    if n == 0:
        return 0

    # pearson correlation calculations
    sum1 = sum([m1[keyname] for keyname in si])
    sum2 = sum([m2[keyname] for keyname in si])
    sum1Sq = sum([pow(m1[keyname],2) for keyname in si])
    sum2Sq = sum([pow(m2[keyname],2) for keyname in si])
    pSum = sum([m1[keyname]*m2[keyname] for keyname in si])
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0:
        return 0
    r=num/den
    return r

# bicluster class ------------------------------------------------
class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left=left
        self.right=right
        self.vec=vec
        self.id=id
        self.distance=distance

# generating cluster
def hcluster(






# Run Application ----------------------------------------------------------
def main():
    global cities
    cities = ['lasvegas', 'losangeles', 'sfbay', 'seoul', 'tokyo','london']    
    subjects = getSubjectPerCity( 'jjj' ) # jjj is jobs
    result = sortData( subjects, 1 ) # type 0 for acending, 1 for normalized

    pprint.pprint( result )
    print sim_pearson(result['losangeles'], result['tokyo'])
    print sim_pearson(result['seoul'], result['tokyo'])

if __name__ == "__main__":
    main()
