from neo4j.v1 import GraphDatabase
import csv
from itertools import islice
import networkx as nx
from networkx.algorithms import bipartite as bi
import math
import matplotlib.pyplot as plt

class OpenFlights(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query):
        with self._driver.session() as session:
            return session.run(query)

if __name__ == '__main__':
    neo = OpenFlights('bolt://localhost:7687', 'neo4j', 'password')

    # neo.query('Match (n) DETACH DELETE n')
    # neo.query('CREATE CONSTRAINT ON (r:Airport) ASSERT r.id IS UNIQUE')
    # neo.query('CREATE CONSTRAINT ON (c:City) ASSERT c.loc IS UNIQUE')
    #
    # # add all cities and airports to database
    # with open('openflights_airports.txt', newline='') as csvfile:
    #     next(islice(csvfile, 1, 1), None)
    #     for r in csv.reader(csvfile, delimiter = ' '):
    #         r[1] = r[1].replace("'", "")
    #         r[2] = r[2].replace("'", "")
    #         r[3] = r[2] + ', ' + r[3].replace("'", "")
    #         neo.query(f"MERGE (c:City {{loc: '{r[3]}' }}) ")
    #         neo.query(f"MERGE (:Airport {{id: '{r[0]}', name: '{r[1]}', lat: '{r[6]}', lon: '{r[7]}'}})")
    #         neo.query(f"MATCH (a:Airport {{id: '{r[0]}' }}) \
    #                   WITH a \
    #                   MATCH (c:City {{loc: '{r[3]}' }}) \
    #                   WITH a, c \
    #                   MERGE (a)-[:LOCATED {{weight: '1'}}]->(c)")
    #
    # #add all airports and connect to cities
    # with open('openflights.txt', newline='') as csvfile:
    #     for r in csv.reader(csvfile, delimiter=' '):
    #         neo.query(f"MATCH (a1:Airport {{id: '{r[0]}' }}) \
    #                     WITH a1 \
    #                     MATCH (a2: Airport {{id: '{r[1]}' }}) \
    #                     WITH a1, a2 \
    #                     MATCH (a1)-[:LOCATED]->(c1:City) \
    #                     WITH a1, a2, c1 \
    #                     MATCH (a2)-[:LOCATED]->(c2:City) \
    #                     MERGE (a1)-[:CONNECTS {{weight: '{r[2]}'}}]->(c2) \
    #                     MERGE (a2)-[:CONNECTS {{weight: '{r[2]}'}}]->(c1)")

    g = nx.Graph()

    results = neo.query('MATCH (a:Airport)-[c]->(b:City),'
                        '(b)<-[]-(a2:Airport) \
                         WHERE b.loc ENDS WITH "United Kingdom" \
                        AND a <> a2 \
                       RETURN a.id, b.loc, c.weight')

    # results = neo.query('MATCH (a:Airport)-[c]->(b:City)\
    #                     WHERE b.loc ENDS WITH "United States" \
    #                     OR b.loc ENDS WITH "Canada" \
    #                    RETURN a.id, b.loc, c.weight')
    #usa
    # results = [(a, b.split(',')[0], c) for a, b, c in results]

    airports = []
    cities = []

    for r in results:
        if r[0] not in airports:
            airports.append(r[0])
        if r[1] not in cities:
            cities.append(r[1])
        g.add_edge(r[0], r[1], weight=r[2])
    g.add_nodes_from(airports, bipartite=0)
    g.add_nodes_from(cities, bipartite=1)

    # widths = [int(edata['weight']) for f, t, edata in g.edges(data=True)]
    # n_color = ['b' if x in airports else 'g' for x in g.nodes()]
    # pos = nx.spring_layout(g)
    # nx.draw_networkx(g, with_labels=True, node_color=n_color, width=widths, edge_color=widths, pos=pos)
    # plt.show()

    # nx.write_gexf(g, 'uk.gexf')

    two = bi.weighted_projected_graph(g, cities, ratio=False)
    widths = [int(edata['weight']) for f, t, edata in two.edges(data=True)]

    # nx.draw_networkx(two, width=widths, edge_color=widths)
    # plt.show()

    nx.write_gexf(two, 'uk_cities.gexf')

    # def trim_edges(g, weight=1):
    #     g2 = nx.Graph()
    #     # g2.add_nodes_from(g.nodes(data=True))
    #     for f, t, edata in g.edges(data=True):
    #         if edata['weight'] > weight:
    #             g2.add_edge(f, t, weight=edata['weight'])
    #     return g2
    #
    # def island_method(g, iterations = 10):
    #     weights = [int(edata['weight']) for f, to, edata in g.edges(data=True)]
    #     mn = int(min(weights))
    #     mx = int(max(weights))
    #     step = int((mx-mn)/iterations)
    #
    #     return [[threshold, trim_edges(g, threshold)] for threshold in range(mn, mx, step)]
    #
    # islands = island_method(two)
    # for i in islands:
    #     print(i[0], len(i[1]), len(list(nx.connected_component_subgraphs(i[1]))))
    #
    # to_disp = trim_edges(two, weight=78)
    # for part in nx.connected_component_subgraphs(to_disp):
    #     widths = [int(edata['weight'])/100 for f, t, edata in part.edges(data=True)]
    #     nx.draw_networkx(part, width=widths, edge_color=widths)
    #     plt.show()














