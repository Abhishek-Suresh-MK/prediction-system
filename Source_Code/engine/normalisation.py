class LaptopNormalizer:
    def __init__(self, laptops, criteria):
        """
        laptops: list of laptop dictionaries
        criteria: dict -> { "price": "cost", "performance": "beneficial", ... }
        """
        self.laptops = laptops
        self.criteria = criteria
        self.bounds = self._calculate_bounds()

    def _calculate_bounds(self):
        """Calculate min & max for each criterion."""
        bounds = {}
        for key in self.criteria.keys():
            values = [lap[key] for lap in self.laptops if key in lap]

            if not values:
                raise ValueError(f"No values found for criterion: {key}")

            bounds[key] = {
                "min": min(values),
                "max": max(values)
            }
        return bounds

    def normalize_all(self):
        """
        Returns new list with normalized values added.
        Does NOT destroy original values.
        """
        normalized_laptops = []

        for lap in self.laptops:
            norm_lap = lap.copy()  # keep original data

            for key, ctype in self.criteria.items():
                val = lap[key]
                min_v = self.bounds[key]["min"]
                max_v = self.bounds[key]["max"]

                # Avoid division by zero (if all laptops have the same value)
                if max_v == min_v:
                    norm_value = 1.0
                else:
                    if ctype == "beneficial":
                        # Normalization: (value - min) / (max - min)
                        norm_value = (val - min_v) / (max_v - min_v)
                    elif ctype == "cost":
                        # Normalization: (max - value) / (max - min)
                        norm_value = (max_v - val) / (max_v - min_v)
                    else:
                        raise ValueError(f"Invalid criteria type: {ctype}")

                # Store normalized value with a suffix
                norm_lap[f"{key}_normalized"] = norm_value

            normalized_laptops.append(norm_lap)

        return normalized_laptops
