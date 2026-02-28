def generate_explanation(ranked_laptops, user_weights):
    if not ranked_laptops:
        return "No laptops available."

    top = ranked_laptops[0]
    score = top["final_score"]
    name = top["name"]

    highest_criterion = max(user_weights, key=user_weights.get)

    return (
        f"{name} is recommended as the best option. "
        f"It achieved the highest weighted score of {score}. "
        f"Your most important criterion was '{highest_criterion}', "
        f"which strongly influenced the final ranking."
    )