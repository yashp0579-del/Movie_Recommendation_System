"""Rule-based recommendation engine (no ML) - pure IF/THEN scoring rules."""
import pandas as pd

ERAS = {
    "Any": (0, 9999),
    "Classic (before 1990)": (0, 1989),
    "1990s": (1990, 1999),
    "2000s": (2000, 2009),
    "2010s": (2010, 2019),
    "2020s": (2020, 9999),
}


def load_movies(path="movies.csv"):
    df = pd.read_csv(path)
    df["genres"] = df["genre"].str.split("|")
    df["moods"] = df["mood"].str.split("|")
    return df


def recommend(df, genres, moods, language, min_rating, max_duration, era, top_n=12):
    """Apply hard filter rules first, then soft scoring rules.
    Returns list of (row, score, reasons)."""
    lo, hi = ERAS[era]
    results = []
    for _, m in df.iterrows():
        # ---- HARD RULES (movie is rejected if any fails) ----
        if language != "Any" and m["language"] != language:
            continue
        if m["rating"] < min_rating:
            continue
        if m["duration"] > max_duration:
            continue
        if not (lo <= m["year"] <= hi):
            continue

        # ---- SOFT RULES (add score + explanation) ----
        score, reasons = 0.0, []
        g_match = [g for g in genres if g in m["genres"]]
        m_match = [x for x in moods if x in m["moods"]]
        if g_match:
            score += 3 * len(g_match)
            reasons.append("Genre match: " + ", ".join(g_match))
        if m_match:
            score += 3 * len(m_match)
            reasons.append("Fits your mood: " + ", ".join(m_match))
        if (genres or moods) and not (g_match or m_match):
            continue  # user chose preferences but nothing matches
        if m["rating"] >= 8.5:
            score += 2
            reasons.append("Top rated")
        elif m["rating"] >= 8.0:
            score += 1
            reasons.append("Highly rated")
        score += m["rating"] / 10
        results.append((m, round(score, 2), reasons))

    results.sort(key=lambda r: r[1], reverse=True)
    return results[:top_n]


def similar_movies(df, title, top_n=8):
    """Rule: same genre +3, same mood +2, same director +4, same language +1."""
    base = df[df["title"] == title].iloc[0]
    out = []
    for _, m in df.iterrows():
        if m["title"] == title:
            continue
        score, reasons = 0, []
        gs = set(base["genres"]) & set(m["genres"])
        ms = set(base["moods"]) & set(m["moods"])
        if gs:
            score += 3 * len(gs)
            reasons.append("Shared genre: " + ", ".join(sorted(gs)))
        if ms:
            score += 2 * len(ms)
            reasons.append("Similar mood: " + ", ".join(sorted(ms)))
        if m["director"] == base["director"]:
            score += 4
            reasons.append(f"Same director: {m['director']}")
        if m["language"] == base["language"]:
            score += 1
        if score > 0:
            score += m["rating"] / 10
            out.append((m, round(score, 2), reasons))
    out.sort(key=lambda r: r[1], reverse=True)
    return out[:top_n]