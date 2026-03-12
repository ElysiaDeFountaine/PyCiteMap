import re
import pandas as pd


STOPWORDS = {
    "study", "analysis", "method", "methods", "article", "research",
    "human", "humans", "male", "female", "adult", "aged"
}


def normalize_keyword(keyword: str) -> str:
    keyword = keyword.lower().strip()
    keyword = re.sub(r"[^a-z0-9\s\-]", "", keyword)
    keyword = re.sub(r"\s+", " ", keyword)

    synonym_map = {
        "artificial intelligence": "ai",
        "machine learning": "machine learning",
        "elderly care": "elderly care",
        "older adults": "elderly",
        "aged": "elderly",
        "health care": "healthcare",
    }

    return synonym_map.get(keyword, keyword)


def extract_keywords_from_concepts(concepts):
    keywords = []
    if not isinstance(concepts, list):
        return keywords

    for c in concepts:
        name = c.get("display_name")
        score = c.get("score", 0)
        if not name:
            continue
        if score < 0.3:
            continue

        kw = normalize_keyword(name)
        if len(kw) <= 2:
            continue
        if kw in STOPWORDS:
            continue
        keywords.append(kw)

    return list(set(keywords))


def extract_keywords_column(df: pd.DataFrame):
    return df["concepts"].apply(extract_keywords_from_concepts)