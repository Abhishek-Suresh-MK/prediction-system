class LaptopNormalizer:
    """
    Min-max normalisation for all scored criteria.
    For 'cost' criteria (price, weight), lower raw = higher norm.
    For 'beneficial' criteria, higher raw = higher norm.
    """

    def __init__(self, laptops, criteria):
        self.laptops = laptops
        self.criteria = criteria
        self.bounds = self._calculate_bounds()

    def _calculate_bounds(self):
        bounds = {}
        for key in self.criteria.keys():
            values = [lap[key] for lap in self.laptops if key in lap]
            if not values:
                continue
            bounds[key] = {
                "min": min(values),
                "max": max(values)
            }
        return bounds

    def normalize_all(self):
        normalized = []
        for lap in self.laptops:
            new_lap = lap.copy()
            for key, meta in self.criteria.items():
                ctype = meta["type"]
                if key not in self.bounds:
                    new_lap[f"{key}_normalized"] = 0.0
                    continue
                min_v = self.bounds[key]["min"]
                max_v = self.bounds[key]["max"]
                val = lap.get(key, min_v)

                if max_v == min_v:
                    norm_value = 1.0
                else:
                    if ctype == "beneficial":
                        norm_value = (val - min_v) / (max_v - min_v)
                    else:  # cost
                        norm_value = (max_v - val) / (max_v - min_v)

                new_lap[f"{key}_normalized"] = round(norm_value, 4)
            normalized.append(new_lap)
        return normalized