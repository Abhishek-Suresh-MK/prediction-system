class LaptopScorer:
    def __init__(self, normalized_laptops, user_weights):
        self.laptops = normalized_laptops
        self.user_weights = self._normalize_weights(user_weights)

    def _normalize_weights(self, weights):
        total = sum(weights.values())
        if total == 0:
            raise ValueError("All weights cannot be zero.")
        return {k: v / total for k, v in weights.items()}

    def calculate_scores(self):
        for lap in self.laptops:
            score = 0.0
            for criterion, weight in self.user_weights.items():
                score += lap[f"{criterion}_normalized"] * weight

            lap["final_score"] = round(score, 4)

        return self.laptops