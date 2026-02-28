from flask import Flask, render_template, request

from engine.loader import LaptopLoader
from engine.normalisation import LaptopNormalizer
from engine.scorer import LaptopScorer
from engine.ranker import rank_laptops
from engine.explain import generate_explanation

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        budget = float(request.form.get("budget"))

        user_weights = {
            "price": float(request.form.get("price")),
            "performance": float(request.form.get("performance")),
            "battery": float(request.form.get("battery")),
            "weight": float(request.form.get("weight"))
        }

        custom_laptop = None
        if request.form.get("custom_name"):
            custom_laptop = {
                "name": request.form.get("custom_name"),
                "price": float(request.form.get("custom_price")),
                "performance": float(request.form.get("custom_performance")),
                "battery": float(request.form.get("custom_battery")),
                "weight": float(request.form.get("custom_weight"))
            }

        loader = LaptopLoader()
        laptops, criteria = loader.get_combined_data(custom_laptop)

        filtered = [lap for lap in laptops if lap["price"] <= budget]

        if not filtered:
            return render_template("result.html", ranked=[], explanation="No laptops within budget.")

        normalizer = LaptopNormalizer(filtered, criteria)
        normalized = normalizer.normalize_all()

        scorer = LaptopScorer(normalized, user_weights)
        scored = scorer.calculate_scores()

        ranked = rank_laptops(scored)

        explanation = generate_explanation(ranked, user_weights)

        return render_template("result.html", ranked=ranked, explanation=explanation)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)