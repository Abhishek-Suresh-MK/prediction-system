CRITERION_LABELS = {
    "price": "Price",
    "cpu_score": "CPU Performance",
    "gpu_score": "GPU / Graphics",
    "ram_score": "RAM",
    "storage_score": "Storage",
    "battery": "Battery Life",
    "weight": "Portability",
    "display_score": "Display Quality"
}

CRITERION_UNITS = {
    "price": "₹",
    "cpu_score": "pts",
    "gpu_score": "pts",
    "ram_score": "pts",
    "storage_score": "pts",
    "battery": "hrs",
    "weight": "kg",
    "display_score": "pts"
}


def generate_explanation(ranked_laptops, user_weights, criteria):
    """
    Generates a structured explanation dict for the top laptop, including:
    - Why it won (top contributing criteria)
    - How it beat #2 (delta analysis)
    - Any notable weaknesses
    - Per-criterion breakdown
    """
    if not ranked_laptops:
        return {"summary": "No laptops available.", "details": [], "warnings": []}

    winner = ranked_laptops[0]
    active_weights = {k: v for k, v in user_weights.items() if v > 0}

    # --- Build per-criterion breakdown ---
    breakdown = []
    for criterion, weight_pct in sorted(active_weights.items(), key=lambda x: x[1], reverse=True):
        label = CRITERION_LABELS.get(criterion, criterion)
        unit = CRITERION_UNITS.get(criterion, "")
        raw_val = winner.get(criterion, "N/A")
        norm_val = winner.get(f"{criterion}_normalized", 0)
        contribution = winner.get("criterion_contributions", {}).get(criterion, 0)

        # Average across all ranked laptops
        avg_raw = sum(l.get(criterion, 0) for l in ranked_laptops) / len(ranked_laptops)

        ctype = criteria.get(criterion, {}).get("type", "beneficial")
        if ctype == "beneficial":
            vs_avg = "above average" if raw_val > avg_raw else "below average"
        else:
            vs_avg = "above average" if raw_val < avg_raw else "below average"

        breakdown.append({
            "criterion": label,
            "weight_pct": weight_pct,
            "raw_value": raw_val,
            "unit": unit,
            "norm_score": round(norm_val * 100, 1),
            "contribution_pct": round(contribution * 100, 1),
            "vs_avg": vs_avg
        })

    # --- Delta vs second place ---
    vs_second = None
    if len(ranked_laptops) >= 2:
        second = ranked_laptops[1]
        delta = round(winner["final_score"] - second["final_score"], 4)
        # Find criterion where winner gained most over second
        contribs_winner = winner.get("criterion_contributions", {})
        contribs_second = second.get("criterion_contributions", {})
        decisive = max(
            active_weights.keys(),
            key=lambda c: (contribs_winner.get(c, 0) - contribs_second.get(c, 0))
        )
        decisive_label = CRITERION_LABELS.get(decisive, decisive)
        margin = "narrow" if delta < 0.02 else "clear" if delta < 0.07 else "strong"
        vs_second = {
            "name": second["name"],
            "delta": delta,
            "margin": margin,
            "decisive_criterion": decisive_label
        }

    # --- Warnings: user weighted something but winner scored low there ---
    warnings = []
    for criterion, weight_pct in active_weights.items():
        if weight_pct >= 15:
            norm_val = winner.get(f"{criterion}_normalized", 0)
            if norm_val < 0.4:
                label = CRITERION_LABELS.get(criterion, criterion)
                warnings.append(
                    f"Note: You weighted '{label}' at {weight_pct}%, "
                    f"but the top laptop scored only {round(norm_val*100,1)}% on this criterion — "
                    f"consider increasing your budget or adjusting priorities."
                )

    # --- Top strengths ---
    top_strengths = [b["criterion"] for b in breakdown[:3] if b["norm_score"] >= 60]

    summary = _build_summary(winner, vs_second, top_strengths, warnings)

    return {
        "summary": summary,
        "breakdown": breakdown,
        "vs_second": vs_second,
        "warnings": warnings,
        "top_strengths": top_strengths
    }


def _build_summary(winner, vs_second, top_strengths, warnings):
    name = winner["name"]
    score = winner["final_score"]

    lines = [f"<strong>{name}</strong> earned the top recommendation with a utility score of {score}."]

    if top_strengths:
        lines.append(f"Its strongest advantages are in: {', '.join(top_strengths)}.")

    if vs_second:
        second_name = vs_second['name']
        margin = vs_second['margin']
        decisive = vs_second['decisive_criterion']
        delta = vs_second['delta']
        lines.append(
            f"It beat <strong>{second_name}</strong> by a {margin} margin ({delta} points), "
            f"with <em>{decisive}</em> being the most decisive factor."
        )

    if warnings:
        lines.append("⚠ " + warnings[0])

    return " ".join(lines)