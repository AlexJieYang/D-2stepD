"""Directed disruption metrics and graph input adapters."""
import igraph as ig
import numpy as np
from project_utils import input_path, load_table

def aps_graph(edges, nodes):
    if nodes["id"].isna().any() or nodes["id"].duplicated().any():
        raise ValueError("APS node ids must be present and unique")
    lookup = dict(zip(nodes["id"], range(len(nodes))))
    pairs = edges[["citing_doi", "cited_doi"]].apply(lambda s: s.map(lookup))
    if pairs.isna().any().any():
        raise ValueError("Every cited/citing DOI must occur in aps_nodes.id")
    graph = ig.Graph(n=len(nodes), edges=pairs.astype(int).itertuples(index=False, name=None), directed=True)
    graph.simplify(multiple=True, loops=True)
    return graph

def calculate_cd(graph, focal):
    citers = set(graph.predecessors(focal)) - {focal}
    references = set(graph.successors(focal)) - {focal}
    if not citers:
        return 0.0, 0.0
    if not references:
        return 1.0, 1.0
    reference_citers = set().union(*(set(graph.predecessors(v)) for v in references)) - {focal}
    ni = len(citers - reference_citers)
    nj = len(citers & reference_citers)
    nk = len(reference_citers - citers)
    denominator = ni + nj + nk
    return ni / denominator, (ni - nj) / denominator

def calculate_2d(graph, focal):
    references = set(graph.successors(focal)) - {focal}
    if not references:
        return 1.0
    second = set().union(*(set(graph.successors(v)) for v in references)) - {focal}
    if not second:
        return 1.0
    related = set().union(*(set(graph.predecessors(v)) for v in second)) - {focal}
    citers = set(graph.predecessors(focal)) - {focal}
    denominator = len(citers | related)
    return len(citers - related) / denominator if denominator else 0.0

def network_input(name):
    metrics = load_table(name + "_metrics")
    rows = []
    for line in input_path(name + "_edges").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 2:
            raise ValueError("Each edge line needs at least two vertex IDs")
        source, target = map(int, fields[:2])
        if min(source, target) < 0 or max(source, target) >= len(metrics):
            raise ValueError("Metric row positions must cover all edge vertex IDs")
        rows.append((target, source))
    graph = ig.Graph(n=len(metrics), edges=rows, directed=True)
    graph.simplify(multiple=True, loops=True)
    return graph, metrics
