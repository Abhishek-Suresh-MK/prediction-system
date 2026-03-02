CRITERION_LABELS = {
    "price":         "Price",
    "cpu_score":     "CPU / Processor",
    "gpu_score":     "GPU / Graphics",
    "ram_score":     "RAM",
    "storage_score": "Storage",
    "battery":       "Battery Life",
    "weight":        "Portability",
    "display_score": "Display Quality"
}

CRITERION_UNITS = {
    "price":         "₹",
    "cpu_score":     "",        # processor name needs no unit suffix
    "gpu_score":     "pts",
    "ram_score":     "pts",
    "storage_score": "pts",
    "battery":       "hrs",
    "weight":        "kg",
    "display_score": "pts"
}


def generate_explanation(ranked_laptops, user_weights, criteria):
    """
    Generates a structured explanation dict for the top laptop:
    - Per-criterion breakdown (shows processor name for cpu_score row)
    - Delta analysis vs second place
    - Warnings for heavily-weighted but low-scoring criteria
    """
    if not ranked_laptops:
        return {"summary": "No laptops available.", "breakdown": [], "warnings": []}

    winner         = ranked_laptops[0]
    active_weights = {k: v for k, v in user_weights.items() if v > 0}

    # ── Per-criterion breakdown ───────────────────────────────────
    breakdown = []
    for criterion, weight_pct in sorted(active_weights.items(), key=lambda x: x[1], reverse=True):
        label        = CRITERION_LABELS.get(criterion, criterion)
        unit         = CRITERION_UNITS.get(criterion, "")
        raw_val      = winner.get(criterion, "N/A")   # numeric by default
        norm_val     = winner.get(f"{criterion}_normalized", 0)
        contribution = winner.get("criterion_contributions", {}).get(criterion, 0)

        # Keep numeric value for the vs_avg comparison
        numeric_raw = raw_val

        # For the CPU criterion, display the processor name string instead of the number
        if criterion == "cpu_score":
            processor_name = winner.get("cpu")
            if processor_name:
                raw_val = processor_name
                unit    = ""   # no unit suffix next to a processor name

        # Average of the numeric field across all pool laptops
        avg_raw = sum(l.get(criterion, 0) for l in ranked_laptops) / len(ranked_laptops)

        ctype = criteria.get(criterion, {}).get("type", "beneficial")
        try:
            if ctype == "beneficial":
                vs_avg = "above average" if float(numeric_raw) > avg_raw else "below average"
            else:
                vs_avg = "above average" if float(numeric_raw) < avg_raw else "below average"
        except (TypeError, ValueError):
            vs_avg = "—"

        breakdown.append({
            "criterion":        label,
            "weight_pct":       weight_pct,
            "raw_value":        raw_val,
            "unit":             unit,
            "norm_score":       round(norm_val * 100, 1),
            "contribution_pct": round(contribution * 100, 1),
            "vs_avg":           vs_avg
        })

    # ── Delta vs second place ─────────────────────────────────────
    vs_second = None
    if len(ranked_laptops) >= 2:
        second          = ranked_laptops[1]
        delta           = round(winner["final_score"] - second["final_score"], 4)
        contribs_winner = winner.get("criterion_contributions", {})
        contribs_second = second.get("criterion_contributions", {})
        decisive        = max(
            active_weights.keys(),
            key=lambda c: contribs_winner.get(c, 0) - contribs_second.get(c, 0)
        )
        margin    = "narrow" if delta < 0.02 else "clear" if delta < 0.07 else "strong"
        vs_second = {
            "name":               second["name"],
            "delta":              delta,
            "margin":             margin,
            "decisive_criterion": CRITERION_LABELS.get(decisive, decisive)
        }

    # ── Warnings: high weight, low winner score ───────────────────
    warnings = []
    for criterion, weight_pct in active_weights.items():
        if weight_pct >= 15:
            norm_val = winner.get(f"{criterion}_normalized", 0)
            if norm_val < 0.4:
                warnings.append(
                    f"Note: You weighted '{CRITERION_LABELS.get(criterion, criterion)}' at {weight_pct}%, "
                    f"but the top laptop scored only {round(norm_val * 100, 1)}% on this criterion — "
                    f"consider increasing your budget or adjusting priorities."
                )

    top_strengths = [b["criterion"] for b in breakdown[:3] if b["norm_score"] >= 60]

    return {
        "summary":       _build_summary(winner, vs_second, top_strengths, warnings),
        "breakdown":     breakdown,
        "vs_second":     vs_second,
        "warnings":      warnings,
        "top_strengths": top_strengths
    }


def _build_summary(winner, vs_second, top_strengths, warnings):
    lines = [
        f"<strong>{winner['name']}</strong> earned the top recommendation "
        f"with a utility score of {winner['final_score']}."
    ]
    if top_strengths:
        lines.append(f"Its strongest advantages are in: {', '.join(top_strengths)}.")
    if vs_second:
        lines.append(
            f"It beat <strong>{vs_second['name']}</strong> by a {vs_second['margin']} margin "
            f"({vs_second['delta']} points), with <em>{vs_second['decisive_criterion']}</em> "
            f"being the most decisive factor."
        )
    if warnings:
        lines.append("⚠ " + warnings[0])
    return " ".join(lines)