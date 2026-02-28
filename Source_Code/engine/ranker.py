def rank_laptops(scored_laptops):
    ranked = sorted(
        scored_laptops,
        key=lambda x: x["final_score"],
        reverse=True
    )

    for idx, lap in enumerate(ranked, start=1):
        lap["rank"] = idx

    return ranked