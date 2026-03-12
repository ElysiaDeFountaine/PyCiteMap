from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud


def plot_year_trend(year_counts, save_path=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(year_counts["publication_year"], year_counts["count"], marker="o")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Publications")
    ax.set_title("Publication Trend")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_wordcloud(keyword_series, save_path=None):
    all_keywords = []
    for kws in keyword_series:
        if isinstance(kws, list):
            all_keywords.extend(kws)

    freq = Counter(all_keywords)
    if not freq:
        return None

    wc = WordCloud(
        width=1200,
        height=700,
        background_color="white"
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_cooccurrence_network(G, save_path=None):
    if G.number_of_nodes() == 0:
        return None

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.5, seed=42)

    edge_widths = [G[u][v]["weight"] * 0.3 for u, v in G.edges()]
    node_sizes = [200 + 80 * G.degree(n) for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, alpha=0.8, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.4, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    ax.set_title("Keyword Co-occurrence Network")
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_cluster_network(G, communities, save_path=None):
    if G.number_of_nodes() == 0:
        return None

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.5, seed=42)

    community_ids = sorted(set(communities.values()))
    color_map = {cid: idx for idx, cid in enumerate(community_ids)}
    node_colors = [color_map[communities[n]] for n in G.nodes()]
    node_sizes = [200 + 80 * G.degree(n) for n in G.nodes()]
    edge_widths = [G[u][v]["weight"] * 0.3 for u, v in G.edges()]

    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.Set3,
        alpha=0.9,
        ax=ax
    )
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.4, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    ax.set_title("Keyword Cluster Network")
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig