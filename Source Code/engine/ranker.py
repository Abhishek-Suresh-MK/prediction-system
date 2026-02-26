class DecisionScorer:
    # ... (previous methods: __init__, _normalize_weights, calculate_scores)

    def rank_laptops(self, scored_laptops):
        """
        Sort laptops by final_score (descending) and assign rank.

        Input:
            scored_laptops -> list of laptop dicts with 'final_score'

        Output:
            ranked list with rank added
        """
        if not scored_laptops:
            return []

        # Sort by score descending
        # We use a new list (ranked) to avoid mutating the original order 
        # until we are ready to return
        ranked = sorted(
            scored_laptops, 
            key=lambda x: x.get("final_score", 0), 
            reverse=True
        )

        # Assign rank based on the sorted order
        for idx, lap in enumerate(ranked, start=1):
            lap["rank"] = idx

        return ranked
