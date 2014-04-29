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
import dgram  # dendrogram lib

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
            # just in case there is no next page!
            try:
                soupObj = getDataFromUrl( url )
            except:
                break
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
    def __init__(self, map, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.map = map
        self.id = id
        self.distance = distance

# generating hirarchical cluster ---------------------------------
def hcluster( datas ):
    distances = {}
    currentclustid = -1

    clust = []
    i = 0
    for city in datas.keys():
        clust.append(bicluster(datas[city], id = i))
        i += 1
    
    while len(clust) > 1:
        lowestpair = (0,1)
        closest = sim_pearson(clust[0].map, clust[1].map)

        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = sim_pearson(clust[i].map, clust[j].map)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i,j)
        
        ci = []
        for key in clust[lowestpair[0]].map.keys():
            if key in clust[lowestpair[1]].map.keys():
                ci.append(key)

        mergemap = {}
        for keyname in ci:
            mergemap[keyname] = (clust[lowestpair[0]].map[keyname] + clust[lowestpair[1]].map[keyname])/2.0

        newcluster = bicluster(mergemap, left = clust[lowestpair[0]], right = clust[lowestpair[1]], distance = closest, id = currentclustid)

        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]

# Getting Earth's Cities
def getEarthCities(end):
    earth = []
    soupObj = getDataFromUrl("http://www.craigslist.org/about/sites#US")
    links = soupObj('a')
    for link in links[0:end]:
        try:
            ctlink = link['href']
            seq1 = ctlink.split('//')
        except:
            continue
        if seq1[0] == 'http:':
            earth.append(seq1[1].split('.')[0])
    return earth
        
# Hirarchical Print ----------------------------------------------------
def printclust(clust, labels=None, n=0):
    for i in range(n):
        print ' ',
    if clust.id < 0:
        print '-'
    else:
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]
    if clust.left != None:
        printclust(clust.left, labels=labels, n=n+1)
    if clust.right != None:
        printclust(clust.right, labels=labels, n=n+1)

# Run Application ----------------------------------------------------------
def main():
    global cities
#    cities = ['lasvegas', 'losangeles', 'sfbay', 'seoul', 'tokyo','london']    
    cities = getEarthCities(40)
    subjects = getSubjectPerCity( 'jjj' ) # jjj is jobs
    datas = sortData( subjects, 1 ) # type 0 for acending, 1 for normalized

    hclust = hcluster( datas )
    dgram.drawdendrogram(hclust, cities, jpeg = 'craigslist.jpg')
#    printclust( hclust , cities)
#    pprint.pprint( datas )
#    print sim_pearson(datas['losangeles'], datas['tokyo'])
#    print sim_pearson(datas['seoul'], datas['tokyo'])

if __name__ == "__main__":
    main()
