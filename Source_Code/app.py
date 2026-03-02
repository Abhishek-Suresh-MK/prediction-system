import json
import os
import logging
from flask import Flask, render_template, request, jsonify

from engine.loader import LaptopLoader
from engine.normalisation import LaptopNormalizer
from engine.scorer import LaptopScorer
from engine.ranker import rank_laptops, find_category_champions
from engine.explain import generate_explanation

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── App setup ─────────────────────────────────────────────────────
app = Flask(__name__)

# Resolve all config paths relative to this file — safe on any host filesystem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_json(rel_path):
    full = os.path.join(BASE_DIR, rel_path)
    with open(full, "r") as f:
        return json.load(f)

# Load static config once at startup
try:
    PROFILES  = _load_json("config/profiles.json")
    CRITERIA  = _load_json("config/criteria.json")
    SPEC_MAPS = _load_json("config/spec_maps.json")
    logger.info("Config loaded — %d profiles, %d criteria", len(PROFILES), len(CRITERIA))
except Exception as e:
    logger.error("Failed to load config at startup: %s", e)
    raise


# ── Routes ────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """Render health-check endpoint — must return 200."""
    return jsonify({"status": "ok"}), 200


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
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON body."}), 400

        # ── Budget ────────────────────────────────────────────────
        try:
            budget = float(data.get("budget", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Budget must be a number."}), 400

        if budget <= 0:
            return jsonify({"error": "Please enter a valid budget."}), 400

        # ── Mode ──────────────────────────────────────────────────
        mode = data.get("mode", "combined")
        if mode not in ("predefined", "custom", "combined"):
            return jsonify({"error": f"Invalid mode '{mode}'."}), 400

        # ── Weights ───────────────────────────────────────────────
        raw_weights = data.get("weights", {})
        try:
            user_weights = {k: float(v) for k, v in raw_weights.items()}
        except (TypeError, ValueError):
            return jsonify({"error": "All weights must be numbers."}), 400

        total_weight = sum(user_weights.values())
        if abs(total_weight - 100) > 1:
            return jsonify({
                "error": f"Weights must sum to 100. Current total: {round(total_weight, 1)}"
            }), 400

        # ── Custom laptops ────────────────────────────────────────
        custom_laptops = data.get("custom_laptops", [])
        if not isinstance(custom_laptops, list):
            return jsonify({"error": "custom_laptops must be a list."}), 400

        # ── Load & process ────────────────────────────────────────
        loader = LaptopLoader(
            laptops_path=os.path.join(BASE_DIR, "data", "laptops.json"),
            criteria_path=os.path.join(BASE_DIR, "config", "criteria.json"),
        )
        laptops, criteria = loader.get_data(mode=mode, custom_laptops=custom_laptops)

        filtered = [lap for lap in laptops if lap["price"] <= budget]
        if not filtered:
            return jsonify({
                "ranked": [],
                "explanation": {
                    "summary": "No laptops match your budget.",
                    "breakdown": [],
                    "warnings": []
                },
                "champions": {},
                "total_before_filter": len(laptops),
                "total_after_filter": 0
            })

        normalizer = LaptopNormalizer(filtered, criteria)
        normalized  = normalizer.normalize_all()

        scorer = LaptopScorer(normalized, user_weights)
        scored = scorer.calculate_scores()

        ranked    = rank_laptops(scored)
        champions = find_category_champions(ranked)
        champions_names = {k: v["name"] for k, v in champions.items()}
        explanation = generate_explanation(ranked, user_weights, criteria)

        output_laptops = []
        for lap in ranked:
            output_laptops.append({
                "rank":                 lap["rank"],
                "id":                   lap.get("id"),
                "name":                 lap["name"],
                "final_score":          lap["final_score"],
                "price":                lap["price"],
                "cpu":                  lap.get("cpu"),
                "cpu_score":            lap.get("cpu_score"),
                "gpu":                  lap.get("gpu"),
                "gpu_score":            lap.get("gpu_score"),
                "ram":                  lap.get("ram"),
                "ram_score":            lap.get("ram_score"),
                "storage":              lap.get("storage"),
                "storage_score":        lap.get("storage_score"),
                "battery":              lap.get("battery"),
                "weight":               lap.get("weight"),
                "display":              lap.get("display"),
                "display_score":        lap.get("display_score"),
                "category_tags":        lap.get("category_tags", []),
                "criterion_contributions": lap.get("criterion_contributions", {}),
                "normalized": {
                    k: lap.get(f"{k}_normalized", 0) for k in criteria.keys()
                },
            })

        logger.info(
            "recommend: mode=%s budget=%.0f pool=%d/%d winner=%s",
            mode, budget, len(filtered), len(laptops),
            ranked[0]["name"] if ranked else "none"
        )

        return jsonify({
            "ranked":               output_laptops,
            "explanation":          explanation,
            "champions":            champions_names,
            "total_before_filter":  len(laptops),
            "total_after_filter":   len(filtered),
        })

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Unexpected error in /recommend")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


# ── Entry point (dev only — Render uses gunicorn) ─────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)