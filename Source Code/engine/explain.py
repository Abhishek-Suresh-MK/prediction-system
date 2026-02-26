class DecisionScorer:
    # ... (previous methods: __init__, calculate_scores, rank_laptops)

    def generate_explanation(self, ranked_laptops, user_weights):
        """
        Generate explanation for top ranked laptop.

        Inputs:
            ranked_laptops -> list after ranking (contains normalized + final_score)
            user_weights -> dict of user priority weights

        Output:
            explanation string
        """

        if not ranked_laptops:
            return "No laptops available for recommendation."

        top = ranked_laptops[0]
        name = top.get("name", "Selected Laptop")
        score = top.get("final_score", 0)

        # Find highest weighted criterion
        # This identifies what the user cares about most
        sorted_weights = sorted(user_weights.items(), key=lambda x: x[1], reverse=True)
        highest_criterion = sorted_weights[0][0]

        norm_key = f"{highest_criterion}_normalized"
        # We fetch the normalized value of the user's top priority
        performance_val = top.get(norm_key, 0)

        explanation = (
            f"{name} is recommended as the best option based on your preferences. "
            f"It achieved the highest overall weighted score of {score}. "
            f"Your most important criterion was '{highest_criterion}', and this laptop "
            f"performed strongly in that area compared to other available options. "
            f"The final recommendation reflects the best balance across all selected criteria."
        )

        return explanation
