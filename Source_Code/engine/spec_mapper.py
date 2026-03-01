import json
import os


class SpecMapper:
    def __init__(self, spec_maps_path="config/spec_maps.json"):
        self.spec_maps_path = spec_maps_path
        self.maps = self._load_maps()

    def _load_maps(self):
        if not os.path.exists(self.spec_maps_path):
            raise FileNotFoundError(f"Spec maps not found at: {self.spec_maps_path}")
        with open(self.spec_maps_path, "r") as f:
            return json.load(f)

    def map_gpu(self, gpu_string):
        """Map GPU string to numeric score. Fuzzy match if exact not found."""
        gpu_map = self.maps["gpu"]
        if gpu_string in gpu_map:
            return gpu_map[gpu_string]
        # Fuzzy: try substring match
        gpu_lower = gpu_string.lower()
        for key, val in gpu_map.items():
            if key.lower() in gpu_lower or gpu_lower in key.lower():
                return val
        return 10  # default fallback for unknown GPU

    def map_ram(self, ram_string):
        """Map RAM string like '16GB' to numeric score."""
        ram_map = self.maps["ram"]
        # Normalise: strip spaces, uppercase
        normalised = ram_string.strip().upper().replace(" ", "")
        if normalised in ram_map:
            return ram_map[normalised]
        # Try extracting number
        try:
            num = int(''.join(filter(str.isdigit, ram_string)))
            # Find closest
            closest = min(ram_map.keys(), key=lambda k: abs(int(''.join(filter(str.isdigit, k))) - num))
            return ram_map[closest]
        except Exception:
            return 20

    def map_storage(self, storage_string):
        """Map storage string to numeric score."""
        storage_map = self.maps["storage"]
        if storage_string in storage_map:
            return storage_map[storage_string]
        # Fuzzy
        storage_lower = storage_string.lower()
        for key, val in storage_map.items():
            if key.lower() in storage_lower:
                return val
        return 20

    def map_display(self, display_string):
        """Map display spec string to numeric score."""
        display_map = self.maps["display"]
        if display_string in display_map:
            return display_map[display_string]
        # Fuzzy: try substring
        display_lower = display_string.lower()
        for key, val in display_map.items():
            if key.lower() in display_lower:
                return val
        # Fallback based on resolution keywords
        if "4k" in display_lower or "3840" in display_lower:
            return 85
        if "2k" in display_lower or "2560" in display_lower or "2880" in display_lower:
            return 75
        if "oled" in display_lower:
            return 80
        if "1080" in display_lower:
            return 45
        return 30

    def enrich_laptop(self, laptop):
        """
        Take a laptop dict and add _score fields for categorical specs.
        Modifies and returns a copy.
        """
        enriched = laptop.copy()
        enriched["gpu_score"] = self.map_gpu(laptop.get("gpu", "Intel UHD"))
        enriched["ram_score"] = self.map_ram(laptop.get("ram", "8GB"))
        enriched["storage_score"] = self.map_storage(laptop.get("storage", "256GB SSD"))
        enriched["display_score"] = self.map_display(laptop.get("display", "1920x1080 IPS"))
        return enriched