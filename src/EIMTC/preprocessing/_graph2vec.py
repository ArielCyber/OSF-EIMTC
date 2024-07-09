from __future__ import annotations
import networkx as nx
import numpy as np
import random
from math import copysign
from gensim.models.doc2vec import Doc2Vec, TaggedDocument



class Graph2Vec:
    def __init__(self, wl_iteration: int = 2, dimensions: int = 128, epochs: int = 20, workers: int = 4, learning_rate: float = 0.025, min_count: int = 5, down_sample: float = 0.0001, seed: int = 42, ignore_attributes: bool = False, use_node_attributes: bool = True, use_edge_attributes: bool = False):
        '''
        wl_iteration: the number of weisfiler-lehman iteration to use on each root node in the graph.
        dimensions: the size of the output dimension of the vector create from the graph.
        epochs: the number of epochs to train the skip-gram model.
        workers: the number of workers to use in the skip-gram model.
        learning_rate: the rate of the learning for the skip-gram model.
        min_count: the number to ignores all words with total frequncy lower than that.
        down_sample: the threshold for configuring which higher-frequency words are randomly downsampled.
        seed: the random seed to set for the random variables in the graph2vec model.
        ignore_attributes: Boolean True/False value for the usage of graph attributes as part of the method to build weisfiler-lehman graph.
        use_node_attributes: Boolean True/False value for the usage of node attributes as part of the method to build weisfiler-lehman graph.
        use_edge_attributes: Boolean True/False value for the usage of edge attriubtes as part of the method to build weisfiler-lehman graph.
        
        The algorithm is inspired by the paper:
            "Graph2vec: Learning Distributed Representations of Graphs"

        Authors:
            - Annamalai Narayanan
            - Mahinthan Chandramohan
            - Rajasekar Venkatesan
            - Lihui Chen
            - Yang Liu
            - Shantanu Jaiswal

        The code is base on the karateclub graph2vec:
            https://github.com/benedekrozemberczki/karateclub/blob/master/karateclub/graph_embedding/graph2vec.py

        NOTE: Customized Graph2Vec algorithm allowing the use of weights on nodes and edges of the graph
        '''
        self.wl_iteration = wl_iteration
        self.dimensions = dimensions
        self.epochs = epochs
        self.workers = workers
        self.learning_rate = learning_rate
        self.min_count = min_count
        self.down_sample = down_sample
        self.seed = seed
        self.ignore_attributes = ignore_attributes
        self.use_node_attributes = use_node_attributes
        self.use_edge_attributes = use_edge_attributes


    
    def fit(self, graphs: list[nx.classes.Graph]):
        '''
        graphs: list of networkx graphs

        The function given the set of graphs as input and learn to transform into list of vectors.
        Each vector reperesnt a graph which was transformed using weisfiler-lehman and skip-grams.
        '''
        self._set_seed()

        documents = [
            self.weisfeiler_lehman(graph,
                                   wl_iteration=self.wl_iteration,
                                   use_node_attributes=self.use_node_attributes,
                                   use_edge_attributes=self.use_edge_attributes,
                                   ignore_attributes=self.ignore_attributes) for graph in graphs
        ]
        documents = [TaggedDocument(words=doc.split('_'),tags=[str(i)]) for i,doc in enumerate(documents)]

        self.model = Doc2Vec(
                            documents,
                            vector_size=self.dimensions,
                            window=0,
                            min_count=self.min_count,
                            dm=0,
                            sample=self.down_sample,
                            workers=self.workers,
                            epochs=self.epochs,
                            alpha=self.learning_rate,
                            seed=self.seed
                            )

        self._embedding = [self.model.dv[str(i)] for i, _ in enumerate(documents)]

    def infer(self, graphs: list[nx.classes.Graph]):
        '''
        graphs: list of networkx graphs

        The function given the set of graphs as input, transform and return list of vectors.
        '''
        self._set_seed()
    
        documents = [
            self.weisfeiler_lehman(graph,
                                   wl_iteration=self.wl_iteration,
                                   use_node_attributes=self.use_node_attributes,
                                   use_edge_attributes=self.use_edge_attributes,
                                   ignore_attributes=self.ignore_attributes) for graph in graphs
        ]

        embedding = np.array(
            [
            self.model.infer_vector(
                doc.split('_'),alpha=self.learning_rate,min_alpha=0.00001,epochs=self.epochs
            ) for doc in documents
            ]
        )
        return embedding

    def weisfeiler_lehman(self, graph: nx.classes.Graph, wl_iteration: int, use_node_attributes: bool, use_edge_attributes: bool, ignore_attributes: bool):
        '''
        graph: networkx graph
        wl_iteration: the number of weisfiler-lehman iteration to use on each root node in the graph.
        use_node_attributes: Boolean True/False value for the usage of node attributes as part of the method to build weisfiler-lehman graph.
        use_edge_attributes: Boolean True/False value for the usage of edge attriubtes as part of the method to build weisfiler-lehman graph.
        ignore_attributes: Boolean True/False value for the usage of graph attributes as part of the method to build weisfiler-lehman graph.

        NOTE: Customized weisfeiler lehman algorithm allowing the use of weights on nodes and edges of the graph
        '''
        canonical_form = [0]*len(graph.nodes())
        
        if ignore_attributes:
            use_node_attributes = False
            use_edge_attributes = False

        if use_node_attributes:
            feature_vec = [graph.nodes[node]['weight'] for node in graph.nodes()]
        else:
            feature_vec = [1]*len(graph.nodes())

        feature_vec = np.array(feature_vec)

        for _ in range(wl_iteration):
            for node in graph.nodes():
                labels = []
                nebs = graph.neighbors(node)
                for neb in nebs:
                    value = feature_vec[neb]
                    if use_edge_attributes:
                        if isinstance(value,np.ndarray):
                            value = value + copysign(graph.edges[(node,neb)]['weight'],value[0])
                        else:
                            value = value + copysign(graph.edges[(node,neb)]['weight'],value)
                    labels.append(value)

                value = labels[0]
                for i in range(1,len(labels)):
                    value += labels[i]
                canonical_form[node] = value
            feature_vec = canonical_form

        if isinstance(canonical_form[0],np.ndarray):
            new_canonical = []
            for value in canonical_form:
                for v in value:
                    new_canonical.append(v)
            canonical_form = new_canonical
            
        t = list(sorted(map(int,canonical_form),reverse=True))
        st = str(t[0])

        for i in range(1,len(t)):
            st += '_'+str(t[i])

        return st

    def _set_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)
