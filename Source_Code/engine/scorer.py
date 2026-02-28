class DecisionScorer:
    def __init__(self, normalized_laptops, user_weights):
        """
        normalized_laptops: list of laptop dicts (with *_normalized fields)
        user_weights: dict -> {"price": 0.3, "performance": 0.4, ...}
        """
        self.laptops = normalized_laptops
        self.user_weights = self._normalize_weights(user_weights)

    # -----------------------------------------
    # Ensure weights sum to 1
    # -----------------------------------------
    def _normalize_weights(self, weights):
        total = sum(weights.values())

        if total == 0:
            raise ValueError("All weights cannot be zero.")

        return {k: v / total for k, v in weights.items()}

    # -----------------------------------------
    # Compute final weighted score
    # -----------------------------------------
    def calculate_scores(self):
        """
        Adds 'final_score' to each laptop dictionary.
        Returns updated laptop list.
        """
        for lap in self.laptops:
            score = 0.0

            for criterion, weight in self.user_weights.items():
                norm_key = f"{criterion}_normalized"

                if norm_key not in lap:
                    raise KeyError(f"Missing normalized field: {norm_key}")

                score += lap[norm_key] * weight

            lap["final_score"] = round(score, 4)

        return self.laptops
