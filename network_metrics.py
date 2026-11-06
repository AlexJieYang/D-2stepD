"""Directed disruption metrics and graph input adapters."""
import igraph as ig
import numpy as np
import pandas as pd
from project_utils import input_path, load_table, configured_directory

APS_METRICS_FILE = "aps_disruption_metrics.csv"
APS_METRIC_COLUMNS = ["D", "2stepD", "CD", "degree"]


def merge_aps_metrics(nodes, metrics):
    """Attach calculated metrics by DOI while preserving node-table row order."""
    required = ["id", *APS_METRIC_COLUMNS]
    missing = sorted(set(required) - set(metrics.columns))
    if missing:
        raise ValueError(f"APS metrics is missing columns: {missing}")
    for name, frame in [("APS nodes", nodes), ("APS metrics", metrics)]:
        if frame["id"].isna().any() or frame["id"].duplicated().any():
            raise ValueError(f"{name} must have unique, non-null DOI ids")
    if set(nodes["id"]) != set(metrics["id"]):
        raise ValueError("APS metrics and node tables must contain the same DOI ids")
    metrics = metrics[required].copy()
    metrics[APS_METRIC_COLUMNS] = metrics[APS_METRIC_COLUMNS].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(metrics[APS_METRIC_COLUMNS].to_numpy(dtype=float)).all():
        raise ValueError("APS calculated metrics must be finite numeric values")
    properties = nodes.drop(columns=APS_METRIC_COLUMNS, errors="ignore")
    return properties.merge(metrics, on="id", how="left", sort=False, validate="one_to_one")


def load_aps_plot_nodes():
    """Read node properties and the calculated metric table for APS figures."""
    path = configured_directory("output_dir", "outputs", "RESEARCH_OUTPUT_DIR") / APS_METRICS_FILE
    if not path.is_file():
        raise FileNotFoundError(
            f"APS calculated metrics: {path}. Run calculate measures in APS Network.ipynb first."
        )
    return merge_aps_metrics(load_table("aps_nodes"), pd.read_csv(path, dtype={"id": str}))

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
