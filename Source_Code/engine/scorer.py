class LaptopScorer:
    """
    Calculates weighted utility scores.
    User weights are on a 0-100 scale (summing to 100),
    which are normalised internally to 0-1 fractions.
    """

    def __init__(self, normalized_laptops, user_weights):
        self.laptops = normalized_laptops
        self.user_weights = self._normalize_weights(user_weights)
        self.raw_weights = user_weights  # preserve originals for display

    def _normalize_weights(self, weights):
        total = sum(weights.values())
        if total == 0:
            raise ValueError("All weights cannot be zero.")
        return {k: v / total for k, v in weights.items()}

    def calculate_scores(self):
        for lap in self.laptops:
            score = 0.0
            criterion_contributions = {}

            for criterion, weight in self.user_weights.items():
                norm_key = f"{criterion}_normalized"
                norm_val = lap.get(norm_key, 0.0)
                contribution = norm_val * weight
                score += contribution
                criterion_contributions[criterion] = round(contribution, 4)

            lap["final_score"] = round(score, 4)
            lap["criterion_contributions"] = criterion_contributions

        return self.laptops