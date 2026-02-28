from flask import Flask, render_template, request

from engine.loader import LaptopLoader
from engine.normalizer import LaptopNormalizer
from engine.scorer import DecisionScorer
from engine.ranker import rank_laptops
from engine.explain import generate_explanation

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Collect user inputs
        budget = float(request.form.get("budget"))

        user_weights = {
            "price": float(request.form.get("price")),
            "performance": float(request.form.get("performance")),
            "battery": float(request.form.get("battery")),
            "weight": float(request.form.get("weight"))
        }

        # Optional custom laptop
        custom_laptop = None
        if request.form.get("custom_name"):
            custom_laptop = {
                "name": request.form.get("custom_name"),
                "price": float(request.form.get("custom_price")),
                "performance": float(request.form.get("custom_performance")),
                "battery": float(request.form.get("custom_battery")),
                "weight": float(request.form.get("custom_weight"))
            }

    except (ValueError, TypeError):
        return "Invalid input. Please enter valid numeric values."

    # Load data
    loader = LaptopLoader()
    laptops, criteria = loader.get_combined_data(custom_laptop)

    # Apply budget constraint
    filtered_laptops = [lap for lap in laptops if lap["price"] <= budget]

    if not filtered_laptops:
        return render_template("result.html", ranked=[], explanation="No laptops match your budget.")

    # Normalize
    normalizer = LaptopNormalizer(filtered_laptops, criteria)
    normalized = normalizer.normalize_all()

    # Score
    scorer = DecisionScorer(normalized, user_weights)
    scored = scorer.calculate_scores()

    # Rank
    ranked = rank_laptops(scored)

    # Explain
    explanation = generate_explanation(ranked, user_weights)

    return render_template("result.html", ranked=ranked, explanation=explanation)


if __name__ == "__main__":
    app.run(debug=True)