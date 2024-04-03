import requests
from typing import List, Set, Mapping
from os import listdir
from os.path import isfile, join
from pprint import pprint
import csv


class Node:
    name: str
    attributes: List[str] = []

    def __init__(self, name: str, attributes: List[str]):
        self.name = name
        self.attributes = attributes

    def get_name(self):
        return self.name

    def get_attrs(self):
        return self.attributes

    def get_num_attrs(self):
        return len(self.get_attrs())

    def __repr__(self):
        return self.get_name()

    @staticmethod
    def get_distance(first: 'Node', second: 'Node') -> float:
        """Returns the distance between two nodes, determined by the
        percentage of attributes shared between the two. This is from
        the perspective of the node with fewer attributes.

        Args:
            first (Node): First node to compare.
            second (Node): Second node to compare.

        Returns:
            float: proportion of attributes shared from 0 to 1.
        """

        if not first.get_num_attrs() or not second.get_num_attrs():
            return 0

        smaller = first
        bigger = second

        if first.get_num_attrs() > second.get_num_attrs():
            smaller = second
            bigger = first

        attrs_in_bigger = 0

        for attr in smaller.get_attrs():
            if attr in bigger.get_attrs():
                attrs_in_bigger += 1

        # print(attrs_in_bigger / smaller.get_num_attrs())

        return attrs_in_bigger / smaller.get_num_attrs()


nodes: List['Node'] = []

for tournament in [f for f in listdir("tournaments")
                   if isfile(join("tournaments", f))]:
    with open(f"tournaments/{tournament}", "r") as f:
        if "export" in tournament or tournament not in ["palatine.csv", "fremd.csv"]:
            continue
        table = csv.reader(f)
        teams: List[str] = []

        next(table)

        for row in table:
            if row[0].isnumeric():
                teams.append(f"{' '.join(row[2].split(' ')[0:-1])} {row[1]}")
                print(f"{' '.join(row[2].split(' ')[0:-1])} {row[1]}")
            else:
                teams.append(f"{row[0]} {row[2]}")

        nodes.append(Node(tournament, teams))


def cluster_nodes(nodes: List[Node], cutoff: float) -> List[Set[Node]]:
    clusters: List[Set[Node]] = []

    # Add nodes to all clusters satisfyong the cutoff
    for node in nodes:
        # Keep track of whether or not a node has been added to a cluster
        added = False

        # Check all clusters
        for cluster in clusters:
            # Check if the cluster is a match
            if any(Node.get_distance(node, member) >= cutoff for member in cluster):
                cluster.add(node)
                added = True

        # If we haven't added to a cluster, create a new one with this as a seed
        if not added:
            clusters.append({node})

    # Merge clusters that have common nodes
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if clusters[i].intersection(clusters[j]):
                    clusters[i] = clusters[i].union(clusters[j])
                    clusters[j] = set()
                    merged = True
        clusters = [cluster for cluster in clusters if cluster]

    return clusters


def test_cutoffs(nodes: List[Node], step: float = 0.01) -> Mapping[float, float]:
    results: Mapping[float, float] = {}
    cutoff: float = 0

    while cutoff <= 1:
        results[cutoff] = len(cluster_nodes(nodes, cutoff))

        cutoff += step

    return results


if __name__ == "__main__":
    pprint(test_cutoffs(nodes))
    clusters = cluster_nodes(nodes, 0.01)

    for cluster in clusters:
        print(f"Cluster ({len(cluster)})")

        for node in cluster:
            print(node)

        print()
