from matplotlib import pyplot as plt
import networkx as nx
import json

from kvstore import StoreValue
from sutypes import SuTypes, TypeRepr

"""
A graph data structure with nodes and edges

The nodes are type variables while each edge represents equality or another constraint

A path finding algorithm is used to find a path from the start node to the end node, if 
a path is found, then the constraints are satisfiable, otherwise they are not
"""
class Graph:

    nodes = None
    primitive_type_nodes = None

    def __repr__(self) -> str:
        return f"Graph(\n\t{self.nodes}\n)"

    def __init__(self):
        self.nodes = []
        self.primitive_type_nodes = []

        # add primitive types
        for i in self.get_primitive_type_nodes():
            self.add_node(i)
            self.primitive_type_nodes.append(i)

    @classmethod
    def get_primitive_type_nodes(cls):
        return [
            Node("String"),
            Node("Number"),
            Node("Boolean"),
            # TODO: look into better ways to handle Any type on the graph
            Node("Any"), # this is the wildcard type 
            Node("NotApplicable"),
            Node("Never"),
            Node("Function"),
            Node("Object"),
            Node("InBuiltOperator"),
        ]

    @staticmethod
    def get_primitive_type_string():
        return "StringNumberBooleanAnyNotApplicableNeverFunctionObjectInBuiltOperator"

    def get_basal_types(self):
        return self.primitive_type_nodes

    def add_basal_type(self, ty):
        """
        @side-effect: also adds the node to the graph
        """
        if not isinstance(ty, Node):
            raise ValueError("ty must be of type Node")

        existsq = self.find_node(ty.value)
        if existsq is None:
            self.add_node(ty)
            self.primitive_type_nodes.append(ty)


    def get_nodes(self):
        return self.nodes

    def find_node(self, name):
        """
        for node in self.nodes:
            if node.value == name:
                return node
        return None
        """
        for node in self.nodes:
            if node.value == name:
                return node
        return None

    def add_node(self, node):
        """
        @param node: Node instance
        """
        if self.find_node(node.value) is None:
            self.nodes.append(node)

    def add_edge(self, node1, node2):
        """
        @param node1: node value 
        @param node2: node value
        parameters are string values not node instances

        @side-effect: adds an edge bothways
        """
        n1 = self.find_node(node1)
        n2 = self.find_node(node2)

        if n1 is not None and n1 is not None:
            n1.add_edge(n2)
            n2.add_edge(n1)
        else:
            raise Exception("Node not found")

    def are_connected(self, node1, node2):
        n1 = self.find_node(node1)
        n2 = self.find_node(node2)

        if n1 is not None and n2 is not None:
            for edge in n1.get_connected_edges():
                if edge == n2:
                    return True
        return False

    def path_exists(self, node1, node2):
        """
        simple BFS to find a path from node1 to node2
        """
        n1 = self.find_node(node1)
        n2 = self.find_node(node2)

        if n1 is not None and n2 is not None:
            visited = []
            queue = []

            queue.append(n1)

            while len(queue) > 0:
                node = queue.pop(0)
                visited.append(node)

                for edge in node.get_connected_edges():
                    if edge == n2:
                        return True
                    if edge not in visited:
                        queue.append(edge)
                        
        return False

    
    def visualise(self):
        G = nx.Graph()

        for node in self.nodes:
            G.add_node(node.value)
            for edge in node.get_connected_edges():
                G.add_edge(node.value, edge.value)

        pos = nx.spring_layout(G, k=0.95)
        labels = {node.value: node.value for node in self.nodes}

        nx.draw(G, pos, with_labels=True, labels=labels)
        plt.show()

    def normalise(self):
        """
        This shortens the edges from the primitive types

        Before:
            String -> x -> y -> z
        After:
            String -> x
            String -> y
            String -> z
        """
        for node in self.nodes:
            if node.sutype in [SuTypes.String, SuTypes.Number, SuTypes.Boolean]:
                for edge in node.get_connected_edges():
                    if edge.sutype not in [SuTypes.String, SuTypes.Number, SuTypes.Boolean]:
                        for edge2 in edge.get_connected_edges():
                            self.add_edge(node.value, edge2.value)
                        self.nodes.remove(edge)

    def to_json(self) -> dict:
        return {
            "nodes": [
                {
                    "value": node.value,
                    "edges": [edge.value for edge in node.get_connected_edges()]
                }
                for node in self.nodes
            ]
        }

    @classmethod
    def from_json(cls, json_data):
        graph_instance = cls()
        graph_data = json.loads(json_data)

        for node_data in graph_data.get('nodes', []):
            value = node_data.get('value')
            node = Node(value)
            graph_instance.add_node(node)

            edges = node_data.get('edges', [])
            for edge_value in edges:
                edge_node = graph_instance.find_node(edge_value)
                if edge_node:
                    graph_instance.add_edge(value, edge_value)

        return graph_instance


class Node:

    # this is the value of the type i.e. "hello", 12.43
    # this is more of the UUID of the node
    value = None

    # neighbours, what it can see
    edges = None

    def __repr__(self) -> str:
        return f"Node(value = {self.value}, edges = {self.edges})"

    def __init__(self, uuid):
        self.value = uuid
        self.edges = []

    def get_connected_edges(self):
        return self.edges
    
    # type edge = Node
    def add_edge(self, edge):
        """
        @note do not use this method directly, use graph.add_edge instead
        """
        for i in self.edges:
            if i.value == edge.value:
                return # edge already exists
        if self.value != edge.value:
            self.edges.append(edge)

    def propogate_type(self, store, new_type:TypeRepr=None, visited=None, check=False):
        """
        simple DFS to find all connected edges and set their type to new_type if provided
        if new_type is not provided the current node's type is propogated
        """
        if visited is None:
            visited = set()

        if self in visited:
            return
        
        visited.add(self)

        if new_type is not None:
            self.sutype = new_type
        else:
            new_type = self.sutype

        if self.value == '0522ea9ed76c4277a38cbe518a1af134':
            pass
        if self.value not in Graph.get_primitive_type_string():
            store.set_on_type_equivalence(self.value, StoreValue(self.value, self.sutype, new_type), check=check)

        for edge in self.edges:
            edge.propogate_type(store, new_type, visited, check=check)



def test_test():

    graph = Graph()

    node_number = Node("Number")
    node_varx = Node("x")
    node_string = Node("String")
    node_vary = Node("y")


    graph.add_node(node_number)
    graph.add_node(node_varx)
    graph.add_node(node_string)
    graph.add_node(node_vary)

    graph.add_edge("Number", "x")
    graph.add_edge("x", "y")

    assert graph.are_connected("Number", "x") is True
    assert graph.path_exists("Number", "y") is True
    assert graph.are_connected("Number", "String") is False

    print("tests passed")

if __name__ == "__main__":
    test_test()

