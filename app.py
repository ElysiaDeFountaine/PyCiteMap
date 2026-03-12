import os
import argparse
from src.retrieval import fetch_openalex_works
from src.cleaning import clean_works_dataframe
from src.keyword_processing import extract_keywords_column
from src.analysis import (
    build_year_count,
    build_cooccurrence_matrix,
    detect_keyword_communities
)
from src.visualization import (
    plot_year_trend,
    plot_wordcloud,
    plot_cooccurrence_network,
    plot_cluster_network
)


def ensure_dirs():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="PyCiteMap MVP")
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--max-results", type=int, default=200, help="Maximum number of records")
    args = parser.parse_args()

    ensure_dirs()

    print(f"[1/6] Retrieving literature for query: {args.query}")
    raw_df = fetch_openalex_works(args.query, max_results=args.max_results)
    raw_path = "data/raw/openalex_raw.csv"
    raw_df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    print(f"Saved raw data to {raw_path}")

    print("[2/6] Cleaning data")
    clean_df = clean_works_dataframe(raw_df)
    processed_path = "data/processed/openalex_clean.csv"
    clean_df.to_csv(processed_path, index=False, encoding="utf-8-sig")
    print(f"Saved cleaned data to {processed_path}")

    print("[3/6] Extracting keywords")
    clean_df["keywords_list"] = extract_keywords_column(clean_df)

    print("[4/6] Building year trend")
    year_counts = build_year_count(clean_df)
    plot_year_trend(year_counts, save_path="outputs/year_trend.png")

    print("[5/6] Generating word cloud")
    plot_wordcloud(clean_df["keywords_list"], save_path="outputs/wordcloud.png")

    print("[6/6] Building co-occurrence and clustering network")
    G = build_cooccurrence_matrix(clean_df["keywords_list"], min_cooccurrence=2)
    communities = detect_keyword_communities(G)

    plot_cooccurrence_network(G, save_path="outputs/keyword_cooccurrence.png")
    plot_cluster_network(G, communities, save_path="outputs/keyword_cluster.png")

    print("Done. Outputs are saved in ./outputs")


if __name__ == "__main__":
    main()