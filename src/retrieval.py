import requests
import pandas as pd


OPENALEX_BASE_URL = "https://api.openalex.org/works"


def fetch_openalex_works(query: str, max_results: int = 200, per_page: int = 100) -> pd.DataFrame:
    all_records = []
    cursor = "*"

    while len(all_records) < max_results:
        params = {
            "search": query,
            "per-page": min(per_page, max_results - len(all_records)),
            "cursor": cursor
        }

        response = requests.get(OPENALEX_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        meta = data.get("meta", {})

        if not results:
            break

        for item in results:
            primary_location = item.get("primary_location") or {}
            source_info = primary_location.get("source") or {}

            for item in results:
                try:
                    primary_location = item.get("primary_location") or {}
                    source_info = primary_location.get("source") or {}

                    record = {
                        "id": item.get("id"),
                        "doi": item.get("doi"),
                        "title": item.get("display_name") or "",
                        "publication_year": item.get("publication_year"),
                        "cited_by_count": item.get("cited_by_count", 0),
                        "type": item.get("type") or "",
                        "language": item.get("language") or "",
                        "source": source_info.get("display_name") or "",
                        "abstract_inverted_index": item.get("abstract_inverted_index") or {},
                        "concepts": item.get("concepts") or [],
                        "authorships": item.get("authorships") or [],
                    }
                    all_records.append(record)

                except Exception as e:
                    print(f"Skipping one record due to error: {e}")
                    continue

        cursor = meta.get("next_cursor")
        if not cursor:
            break

    return pd.DataFrame(all_records[:max_results])