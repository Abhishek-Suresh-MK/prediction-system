import json
import os
from flask import Flask, render_template, request, jsonify

from engine.loader import LaptopLoader
from engine.normalisation import LaptopNormalizer
from engine.scorer import LaptopScorer
from engine.ranker import rank_laptops, find_category_champions
from engine.explain import generate_explanation

app = Flask(__name__)

# Load profiles and criteria once at startup
with open("config/profiles.json") as f:
    PROFILES = json.load(f)

with open("config/criteria.json") as f:
    CRITERIA = json.load(f)

with open("config/spec_maps.json") as f:
    SPEC_MAPS = json.load(f)


@app.route("/")
def index():
    return render_template("index.html", profiles=PROFILES, criteria=CRITERIA)


@app.route("/api/profiles")
def get_profiles():
    return jsonify(PROFILES)


@app.route("/api/spec_maps")
def get_spec_maps():
    return jsonify(SPEC_MAPS)


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()

        budget = float(data.get("budget", 0))
        if budget <= 0:
            return jsonify({"error": "Please enter a valid budget."}), 400

        mode = data.get("mode", "combined")  # predefined | custom | combined

        # Parse weights (0-100 each, total should = 100)
        raw_weights = data.get("weights", {})
        user_weights = {k: float(v) for k, v in raw_weights.items()}

        total_weight = sum(user_weights.values())
        if abs(total_weight - 100) > 1:
            return jsonify({"error": f"Weights must sum to 100. Current total: {total_weight}"}), 400

        # Parse custom laptops
        custom_laptops = data.get("custom_laptops", [])

        # Load data
        loader = LaptopLoader()
        laptops, criteria = loader.get_data(mode=mode, custom_laptops=custom_laptops)

        # Budget filter
        filtered = [lap for lap in laptops if lap["price"] <= budget]
        if not filtered:
            return jsonify({
                "ranked": [],
                "explanation": {"summary": "No laptops match your budget.", "breakdown": [], "warnings": []},
                "champions": {},
                "total_before_filter": len(laptops),
                "total_after_filter": 0
            })

        # Normalise
        normalizer = LaptopNormalizer(filtered, criteria)
        normalized = normalizer.normalize_all()

        # Score
        scorer = LaptopScorer(normalized, user_weights)
        scored = scorer.calculate_scores()

        # Rank
        ranked = rank_laptops(scored)

        # Category champions
        champions = find_category_champions(ranked)
        champions_names = {k: v["name"] for k, v in champions.items()}

        # Explanation
        explanation = generate_explanation(ranked, user_weights, criteria)

        # Prepare output (clean up internal fields)
        output_laptops = []
        for lap in ranked:
            output_laptops.append({
                "rank": lap["rank"],
                "id": lap.get("id"),
                "name": lap["name"],
                "final_score": lap["final_score"],
                "price": lap["price"],
                "cpu_score": lap.get("cpu_score"),
                "gpu": lap.get("gpu"),
                "gpu_score": lap.get("gpu_score"),
                "ram": lap.get("ram"),
                "ram_score": lap.get("ram_score"),
                "storage": lap.get("storage"),
                "storage_score": lap.get("storage_score"),
                "battery": lap.get("battery"),
                "weight": lap.get("weight"),
                "display": lap.get("display"),
                "display_score": lap.get("display_score"),
                "category_tags": lap.get("category_tags", []),
                "criterion_contributions": lap.get("criterion_contributions", {}),
                "normalized": {k: lap.get(f"{k}_normalized", 0) for k in criteria.keys()}
            })

        return jsonify({
            "ranked": output_laptops,
            "explanation": explanation,
            "champions": champions_names,
            "total_before_filter": len(laptops),
            "total_after_filter": len(filtered)
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)