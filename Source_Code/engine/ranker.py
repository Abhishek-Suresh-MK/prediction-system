def rank_laptops(scored_laptops):
    """Sort by final score descending, assign rank."""
    ranked = sorted(scored_laptops, key=lambda x: x["final_score"], reverse=True)
    for idx, lap in enumerate(ranked, start=1):
        lap["rank"] = idx
    return ranked


def find_category_champions(laptops):
    """
    From the full scored list, find the best laptop for gaming and office
    based on their category_tags (independent of user weights).
    Returns dict with 'gaming' and 'office' keys.
    """
    champions = {}

    gaming = [l for l in laptops if "gaming" in l.get("category_tags", [])]
    office = [l for l in laptops if "office" in l.get("category_tags", [])]

    if gaming:
        champions["gaming"] = max(gaming, key=lambda x: x["final_score"])
    if office:
        champions["office"] = max(office, key=lambda x: x["final_score"])

    return champions