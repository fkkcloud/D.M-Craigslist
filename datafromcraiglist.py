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
import random
from PIL import *

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
                  'year old', 'yrs old', 'from','needed','need','am','pm',\
                  'time']:
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
        for page in ["","100","200"]: #["","100"] to do more pages
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

        maxval = len(sortedDataPerCity[k])
        val = {}                            
        for item in sortedDataPerCity[k]:
            # algorithm key
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
    
    return remap(r, -1.0, 1.0, 0.0, 1.0)

# remapping func -------------------------------------------------
def remap( val, oldmin, oldmax, newmin, newmax ):
    return (((val - oldmin) * (newmax - newmin)) / (oldmax - oldmin)) + newmin

# bicluster class ------------------------------------------------
class bicluster:
    def __init__(self, map, left=None, right=None, distance=0.0, id=None, location=None, com=0):
        self.left = left
        self.right = right
        self.map = map
        self.id = id
        self.distance = distance
        self.city = location
        self.com = com

# generating hirarchical cluster ---------------------------------
def hcluster( datas ):
    distances = {}
    currentclustid = -1

    clust = []
    i = 0
    for city in datas.keys():
        clust.append(bicluster(datas[city], id = i, location = city))
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

        # algorithm key
        # common count dividegetting a city's total count and
        bal = float(len(ci)) / len(datas[datas.keys()[0]]) 

        newcluster = bicluster(mergemap, left = clust[lowestpair[0]], right = clust[lowestpair[1]], distance = closest * bal , id = currentclustid, com = len(ci))

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

# 2D dimensional graph
def mdgraph(data, rate=0.01):
    
    n = len(data)

    # The real distances between every pair of items
    realdist = [[sim_pearson(data[keyname1],data[keyname2]) for keyname1 in data.keys()] for keyname2 in data.keys()]

    outersum = 0.0

    # Randomly initialize the starting points of the locations in 2D
    loc = [[random.random(), random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]

    lasterror = None
    for m in range(0, 1000):
        # Find projected distances
        for i in range(n):
            for j in range(n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))

    # Move points
    grad = [[0.0, 0.0] for i in range(n)]
    
    totalerror = 0
    for k in range(n):
        for j in range(n):
            if j == k: continue
            # The error is percent difference between distances
            try:
                # make sure realdist dataset does not have 0.0
                # which is completely same
                errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
            except:
                errorterm=0

            # Each point needs to be moved away from or towards the other
            # point in proportion to how much error it has
            grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
            grad[k][1]+=((loc[j][1]-loc[j][1])/fakedist[j][k])*errorterm

            # Keep track of the total error
            totalerror+=abs(errorterm)
        print totalerror

        # If the answer got worse by moving the points, we are done
        if lasterror and lasterror < totalerror:
            break
        lasterror = totalerror

        # Move each of the points by the learning rate times the gradient
        for k in range(n):
            loc[k][0] -= rate*grad[k][0]
            loc[k][1] -= rate*grad[k][1]

    return loc

# drawing 2d graph
def draw2d(data, labels, jpeg='mds2d.jpg'):
    
    img = Image.new('RGB', (1000,1000), (255,255,255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 600
        y = (data[i][1] + 0.5) * 600
        draw.text((x,y), labels[i], (0,0,0))
    img.save(jpeg,'JPEG')

        
# Hirarchical Print ----------------------------------------------------
def printclust(clust, labels=None, n=0):
    
    for i in range(n):
        print ' ',
    if clust.id < 0:
        print '-', clust.distance, clust.com
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
    cities = ['lasvegas', 'losangeles', 'sfbay', 'beijing','seoul', 'tokyo',\
                  'london', 'newyork', 'seattle', 'washingtondc', 'chicago',\
                  'sandiego','atlanta','boston','orangecounty','dallas']
#    cities = getEarthCities(20)
    
    subjects = getSubjectPerCity( 'jjj' ) # jjj is jobs
    datas = sortData( subjects, 1 ) # type 0 for acending, 1 for normalized
#    pprint.pprint( datas )
#    hclust = hcluster( datas )

#    printclust( hclust , datas.keys() )

#    dgram.drawdendrogram(hclust, datas.keys(), jpeg = 'craigslist.jpg')
    coords = mdgraph( datas )
    draw2d(coords, datas.keys(), jpeg='craigslist2d.jpg')
#    pprint.pprint( datas )
#    print sim_pearson(datas['losangeles'], datas['tokyo'])
#    print sim_pearson(datas['seoul'], datas['tokyo'])

if __name__ == "__main__":
    main()
