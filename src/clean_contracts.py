import pandas as pd


def clean_contracts(path, signing_year):
    """Load one raw Spotrac free agent CSV and return a cleaned table."""
    df = pd.read_csv(path).dropna(how="all")

    # Spotrac puts a row count in the header (e.g. "Player (168)"), so match by prefix
    player_col = [c for c in df.columns if c.startswith("Player")][0]
    value_col = [c for c in df.columns if c.startswith("Value")][0]
    df = df.rename(columns={
        player_col: "player_name",
        "Pos": "position",
        "Yrs": "years",
        value_col: "total_value",
    })[["player_name", "position", "years", "total_value"]]

    # Strip $ and commas if the values came in as text
    df["total_value"] = pd.to_numeric(
        df["total_value"].astype(str).str.replace(r"[$,]", "", regex=True),
        errors="coerce",
    )
    df["years"] = pd.to_numeric(df["years"], errors="coerce")
    df["signing_year"] = signing_year

    # Qualifying offer flag, then remove the tag from the name
    df["qualifying_offer"] = df["player_name"].str.endswith(" QO", na=False).astype(int)
    df["player_name"] = df["player_name"].str.replace(" QO", "", regex=False).str.strip()

    # Drop rows with no real contract
    df = df[(df["total_value"] > 0) & (df["years"] > 0)].copy()

    # One simple position, hitter or pitcher, and our own AAV
    df["position"] = df["position"].str.split("/").str[0]
    df["player_type"] = df["position"].apply(
        lambda p: "pitcher" if p in ["SP", "RP", "P"] else "hitter"
    )
    df["aav"] = df["total_value"] / df["years"]

    # If a player appears twice, keep the larger contract
    df = (
        df.sort_values("total_value", ascending=False)
          .drop_duplicates(subset="player_name", keep="first")
          .sort_index()
    )
    return df
