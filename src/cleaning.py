import pandas as pd


def clean_works_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning for OpenAlex metadata.
    """
    df = df.copy()

    # remove duplicates
    if "doi" in df.columns:
        df = df.drop_duplicates(subset=["doi"], keep="first")
    else:
        df = df.drop_duplicates(subset=["id"], keep="first")

    # normalize title
    df["title"] = df["title"].fillna("").astype(str).str.strip()

    # normalize year
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    df = df[df["publication_year"].notna()]
    df["publication_year"] = df["publication_year"].astype(int)

    # normalize source/type/language
    for col in ["source", "type", "language"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df.reset_index(drop=True)