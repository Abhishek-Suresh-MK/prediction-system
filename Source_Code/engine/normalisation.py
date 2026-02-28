class LaptopNormalizer:
    def __init__(self, laptops, criteria):
        self.laptops = laptops
        self.criteria = criteria
        self.bounds = self._calculate_bounds()

    def _calculate_bounds(self):
        bounds = {}
        for key in self.criteria.keys():
            values = [lap[key] for lap in self.laptops]
            bounds[key] = {
                "min": min(values),
                "max": max(values)
            }
        return bounds

    def normalize_all(self):
        normalized = []

        for lap in self.laptops:
            new_lap = lap.copy()

            for key, ctype in self.criteria.items():
                min_v = self.bounds[key]["min"]
                max_v = self.bounds[key]["max"]
                val = lap[key]

                if max_v == min_v:
                    norm_value = 1.0
                else:
                    if ctype == "beneficial":
                        norm_value = (val - min_v) / (max_v - min_v)
                    else:  # cost
                        norm_value = (max_v - val) / (max_v - min_v)

                new_lap[f"{key}_normalized"] = norm_value

            normalized.append(new_lap)

        return normalized