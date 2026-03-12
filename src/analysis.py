from collections import Counter, defaultdict
import itertools
import pandas as pd
import networkx as nx
import community as community_louvain


def build_year_count(df: pd.DataFrame) -> pd.DataFrame:
    year_counts = (
        df.groupby("publication_year")
        .size()
        .reset_index(name="count")
        .sort_values("publication_year")
    )
    return year_counts


def build_cooccurrence_matrix(keyword_series, min_cooccurrence: int = 2) -> nx.Graph:
    counter = Counter()

    for keywords in keyword_series:
        if not isinstance(keywords, list):
            continue
        unique_keywords = sorted(set(keywords))
        for pair in itertools.combinations(unique_keywords, 2):
            counter[pair] += 1

    G = nx.Graph()
    for (kw1, kw2), weight in counter.items():
        if weight >= min_cooccurrence:
            G.add_edge(kw1, kw2, weight=weight)

    # remove isolated nodes
    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)

    return G


def detect_keyword_communities(G: nx.Graph):
    if G.number_of_nodes() == 0:
        return {}

    partition = community_louvain.best_partition(G, weight="weight")
    return partition