import networkx as nx
import math
from scipy.stats import circmean
import numpy

def lengthOfAnEdgeIndices(i, j, n, weight=1):
    delta=(2*math.pi/n)* (math.fabs(i-j))
    return math.fabs(2*math.sin(delta/2)*weight)

def lengthOfAnEdge(G, nodesList, n1, n2, weight=1):
    n=len(G.nodes())
    i=nodesList.index(n1)
    j=nodesList.index(n2)
    return lengthOfAnEdgeIndices(i, j, n, weight)

def sumOfEdges(G, nodesList, n):
    sum = 0
    for (u, v, d) in G.edges(n, data='weight'):
        if d==None:d=1
        sum += lengthOfAnEdge(G, nodesList, u, v, d)
    return sum

def totalCost(G, nodesList):
    sum = 0
    for (u, v, d) in G.edges(data='weight'):
        if d==None: d=1
        sum += lengthOfAnEdge(G, nodesList, u, v, d)
    n=len(nodesList)
    minLengths=0
    ni=0
    for node in nx.nodes(G):
        neighbors = nx.all_neighbors(G, node)
        numNeighbors=len(list(neighbors))
        for i in range(1, numNeighbors+1):
            data=G.get_edge_data(ni,i)
            if data==None: weight=1
            else: weight=data.get("weight")
            if weight==None : weight=1
            minLengths+=lengthOfAnEdgeIndices(0, (i+1)//2 , n, weight)
        ni+=1
    minLengths/=(len(G.edges())*2)
    return (sum/len(G.edges())) / minLengths

def totalCostMedianOfAllEdges(G, nodesList):
    edgeslist=[]
    for(u,v,d) in G.edges(data='weight'):
        edgeslist+=[lengthOfAnEdge(G, nodesList, u, v, d)]
    return numpy.median(edgeslist)

def gedIDOfNode(G, node, list):
    return list.index(node)

def getBestID(G, node, nodesList, meanOrMedian):
    neighbors=nx.all_neighbors(G, node)
    indices=[nodesList.index(neighbor) for neighbor in neighbors]
    highest=len(nodesList)
    mean= circmean(indices, high=highest)
    #calculate median
    if not meanOrMedian:
        index= nodesList.index(node)
        sortedIndices=sorted((indices + [index]))
        lenNeighb=len(sortedIndices)
        if lenNeighb %2 ==0:
            median= (int)(lenNeighb/2 + index)%lenNeighb
        else:
            num1=(int)((lenNeighb+1)/2 + index)%lenNeighb
            num2=(int)((lenNeighb-1)/2 + index)%lenNeighb
            median=circmean((num1,num2), high=highest)
    if(math.isnan(mean)):
       mean=nodesList.index(node)
    if meanOrMedian:
        return mean
    else:
        return median

def cutsEdge(e1, e2, n, pos):
    delta = ((e2 - e1) % n + n) % n
    if delta >= n / 2:
        e1,e2=e2,e1
    if e1 <= e2:
        return pos > e1 and pos <= e2
    else:
        return pos > e1 or pos <= e2

#counts number of edges cut if a cut is set on position pos
def numOfCuttedEdges(G, nodeslist, pos, cluster):
    n = len(nodeslist)
    num = 0
    for (u, v, d) in G.edges(cluster, data='weight'):
        if d==None: d=1
        if cutsEdge(nodeslist.index(u), nodeslist.index(v), n, pos):
            num += 1*d
    return num

#calculate where the ratio of cutted edges to possible edges between two clusters is maximal
def calculateBestCut(G, nodeslist, clusters, performedCuts):
    n=len(nodeslist)
    pos=0
    #numMinimalCuts=len(G.edges())
    minRatio=1
    bestPos=0
    cuttedCluster=0
    posInCluster=0
    if performedCuts==[]: # first cut
        minCuts=len(G.edges())
        for i, clist in enumerate(clusters):
            for j in range(len(clist)):
                actCuts=numOfCuttedEdges(G, nodeslist, pos, clist)
                if actCuts<minCuts:
                    minCuts=actCuts
                    bestPos=pos
                    cuttedCluster=i
                    posInCluster=j
                pos+=1
        performedCuts.append(bestPos)
        return bestPos, cuttedCluster, posInCluster, performedCuts
    for i,clist in enumerate(clusters):
        for j in range(len(clist)):
        #for each possible position of a cut
            actNumOfCuttedEdges= numOfCuttedEdges(G, nodeslist, pos, clist)
            actNumOfPossibleEdges= (j+1)*(len(clist)- j)
            actRatio=actNumOfCuttedEdges/actNumOfPossibleEdges
            if actRatio < minRatio and pos not in performedCuts:
                minRatio=actRatio
                bestPos= pos
                cuttedCluster=i
                posInCluster=j

            pos+=1
    performedCuts.append(bestPos)
    return bestPos, cuttedCluster, posInCluster, performedCuts

#perform a cut: make two clusters out of one.
def setCut(G, nodesList, listOfClusters, bestCutTuple):
    clusterToCutNumber=bestCutTuple[1]
    posInCluster=bestCutTuple[2]
    clusterToCut=listOfClusters.pop(clusterToCutNumber)
    listOfClusters.insert(clusterToCutNumber, clusterToCut[posInCluster:])
    listOfClusters.insert(clusterToCutNumber, clusterToCut[:posInCluster])
    return listOfClusters


