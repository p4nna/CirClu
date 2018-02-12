import networkx as nx
import CirCluMethod as c
G = nx.karate_club_graph()
print(c.circlu(G, 2))
