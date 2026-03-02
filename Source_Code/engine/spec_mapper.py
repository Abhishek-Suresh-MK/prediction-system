import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


class SpecMapper:
    def __init__(self, spec_maps_path=None):
        self.spec_maps_path = spec_maps_path or os.path.join(_ROOT, "config", "spec_maps.json")
        self.maps = self._load_maps()

    def _load_maps(self):
        if not os.path.exists(self.spec_maps_path):
            raise FileNotFoundError(f"Spec maps not found at: {self.spec_maps_path}")
        with open(self.spec_maps_path, "r") as f:
            return json.load(f)

    def _cpu_map(self):
        """Return the cpu score dict, filtering comments and non-numeric values."""
        return {
            k: v for k, v in self.maps.get("cpu", {}).items()
            if not k.startswith("_") and isinstance(v, (int, float))
        }

    def _build_cpu_family_index(self):
        """
        Build a family-level fallback index entirely from spec_maps.json["cpu"].
        Averages scores per (family, suffix-tier) group — no hardcoded numbers.
        Returns list of (token, avg_score) sorted longest-first for greedy matching.
        """
        cpu_map = self._cpu_map()
        patterns = []

        # Apple Silicon — longest variant first so 'm3 max' never matches 'm3'
        apple_chips = sorted(
            [k.lower() for k in cpu_map if k.lower().startswith("apple m")],
            key=len, reverse=True
        )
        for chip in apple_chips:
            patterns.append(chip.replace("apple ", ""))  # bare 'm3 pro' also matches

        # Intel Core Ultra
        for tier in ["ultra 9", "ultra 7", "ultra 5"]:
            patterns.append(tier)

        # Intel Core iX with HX / H / U suffix tiers
        for tier in ["core i9", "core i7", "core i5", "core i3"]:
            patterns.append((tier, "hx"))
            patterns.append((tier, "h"))
            patterns.append(tier)

        # AMD Ryzen with HX / H / U suffix tiers
        for tier in ["ryzen 9", "ryzen 7", "ryzen 5", "ryzen 3"]:
            patterns.append((tier, "hx"))
            patterns.append((tier, "h"))
            patterns.append(tier)

        # Qualcomm — longest first
        patterns.append("snapdragon x elite")
        patterns.append("snapdragon x plus")
        patterns.append("snapdragon")

        # Budget Intel
        patterns.append("celeron")
        patterns.append("pentium")

        def matches(key_lower, pattern):
            if isinstance(pattern, tuple):
                family, suffix = pattern
                return family in key_lower and suffix in key_lower
            return pattern in key_lower

        index = []
        for pattern in patterns:
            token  = "-".join(pattern) if isinstance(pattern, tuple) else pattern
            scores = [v for k, v in cpu_map.items() if matches(k.lower(), pattern)]
            if scores:
                index.append((token, round(sum(scores) / len(scores))))

        index.sort(key=lambda x: len(x[0]), reverse=True)
        return index

    def map_cpu(self, cpu_string):
        """
        Map a processor name string → numeric score (0–100).

        Resolution chain:
          1. Exact match in spec_maps.json["cpu"]
          2. Longest substring (known key contained in input)
          3. Reverse substring (input contained in a known key)
          4. Family-average fallback (fully data-driven from JSON)
          5. Median of all known CPU scores (last resort)
        """
        if not cpu_string:
            return 50

        cpu_map = self._cpu_map()

        # 1. Exact
        if cpu_string in cpu_map:
            return cpu_map[cpu_string]

        cpu_lower = cpu_string.lower().strip()

        # 2. Longest substring: a known key appears inside the input
        best_score, best_len = None, 0
        for key, val in cpu_map.items():
            k_lower = key.lower()
            if k_lower in cpu_lower and len(k_lower) > best_len:
                best_score, best_len = val, len(k_lower)
        if best_score is not None:
            return best_score

        # 3. Reverse substring: input appears inside a known key
        for key, val in cpu_map.items():
            if cpu_lower in key.lower():
                return val

        # 4. Family-average fallback
        for token, avg_score in self._build_cpu_family_index():
            if token in cpu_lower:
                return avg_score

        # 5. Median
        all_scores = sorted(cpu_map.values())
        return all_scores[len(all_scores) // 2] if all_scores else 50

    def map_gpu(self, gpu_string):
        """Map GPU string to numeric score. Fuzzy match if exact not found."""
        gpu_map = self.maps.get("gpu", {})
        if gpu_string in gpu_map:
            return gpu_map[gpu_string]
        gpu_lower = gpu_string.lower()
        for key, val in gpu_map.items():
            if key.lower() in gpu_lower or gpu_lower in key.lower():
                return val
        return 10

    def map_ram(self, ram_string):
        """Map RAM string like '16GB' → numeric score."""
        ram_map = self.maps.get("ram", {})
        normalised = ram_string.strip().upper().replace(" ", "")
        if normalised in ram_map:
            return ram_map[normalised]
        try:
            num = int("".join(filter(str.isdigit, ram_string)))
            closest = min(ram_map.keys(), key=lambda k: abs(int("".join(filter(str.isdigit, k))) - num))
            return ram_map[closest]
        except Exception:
            return 20

    def map_storage(self, storage_string):
        """Map storage spec string → numeric score."""
        storage_map = self.maps.get("storage", {})
        if storage_string in storage_map:
            return storage_map[storage_string]
        storage_lower = storage_string.lower()
        for key, val in storage_map.items():
            if key.lower() in storage_lower:
                return val
        return 20

    def map_display(self, display_string):
        """Map display spec string → numeric score."""
        display_map = self.maps.get("display", {})
        if display_string in display_map:
            return display_map[display_string]
        display_lower = display_string.lower()
        for key, val in display_map.items():
            if key.lower() in display_lower:
                return val
        if "4k" in display_lower or "3840" in display_lower:
            return 85
        if "2560" in display_lower or "2880" in display_lower:
            return 75
        if "oled" in display_lower:
            return 80
        if "1080" in display_lower:
            return 45
        return 30

    def enrich_laptop(self, laptop):
        """
        Derive all _score fields from the laptop's human-readable spec strings.
        cpu_score is ALWAYS mapped from the 'cpu' processor string — never read
        from a pre-stored number. This keeps predefined and custom laptops consistent.
        """
        enriched = laptop.copy()
        enriched["cpu_score"]     = self.map_cpu(laptop.get("cpu", ""))
        enriched["gpu_score"]     = self.map_gpu(laptop.get("gpu", "Intel UHD"))
        enriched["ram_score"]     = self.map_ram(laptop.get("ram", "8GB"))
        enriched["storage_score"] = self.map_storage(laptop.get("storage", "256GB SSD"))
        enriched["display_score"] = self.map_display(laptop.get("display", "1920x1080 IPS"))
        return enriched