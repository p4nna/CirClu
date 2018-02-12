import math
import methods as m
from collections import OrderedDict
import networkx as nx

def circlu(G,k):
    G=prepareData(G)
    #list stating which node is at which position
    nodesList=G.nodes()
    totalCostsOld = m.totalCost(G, nodesList)
    totalCostsAct=totalCostsOld
    nodesListOld=nodesList[:]

    #shift nodes until there is no improvement anymore regarding the sum of all edges
    while totalCostsOld>=totalCostsAct:
        nodesListOld=list(nodesList)
        totalCostsOld=totalCostsAct#m.totalCost(G, nodesListOld)
        changed=0
        #for all nodes shift the node to the middle of its neighbors
        for node in G.nodes():
            #calculate actual sum of edges
            initialCosts= m.sumOfEdges(G, nodesList, node)
            initialIndex=nodesList.index(node)
            bestIndex=int(math.floor(m.getBestID(G, node, nodesList, True)))
            if bestIndex!= initialIndex:
                #move node to best Index
                nodesList.remove(node)
                nodesList.insert(bestIndex, node)
                changed+=1
            newCosts=m.sumOfEdges(G , nodesList, node)
            if(newCosts>initialCosts):
                nodesList.remove(node)
                nodesList.insert(initialIndex, node)
                changed-=1
        totalCostsAct=m.totalCost(G, nodesList)
    nodesList=nodesListOld

    #set cuts
    listOfClusters=[nodesList]
    performedCuts=[]
    #up to k clusters
    for i in range(k):
        #where is the best cut
        bestCutTuple=m.calculateBestCut(G, nodesList, listOfClusters, performedCuts)
        performedCuts=bestCutTuple[-1]
        #set cut and actualize listOfClusters, set clusters of nodes.
        listOfClusters=m.setCut(G, nodesList, listOfClusters, bestCutTuple)
    # unify first and last cluster, since we are in a circle
    listOfClusters[0]+=listOfClusters[-1]
    del listOfClusters[-1]

    return listOfClusters

#order nodes according to their degree to receive comparable values
def prepareData(G):
    wishedOrderOfNodesList=sorted(G.nodes(), key=lambda item: G.degree(item))
    wishedOrderOfNodesDict=dict(zip(wishedOrderOfNodesList,range(len(wishedOrderOfNodesList))))
    orderedDictByDegree= OrderedDict(sorted(nx.to_dict_of_dicts(G).items(), key=lambda item: wishedOrderOfNodesDict[item[0]], reverse=True))
    GnewD=nx.from_dict_of_dicts(orderedDictByDegree)
    return GnewD


def circleIndex(G, partition):
    nodeslist=[]
    for part in partition.values():
        for nodeIndex in part:
            nodeslist.append(nodeIndex)
    return m.totalCost(G, nodeslist)