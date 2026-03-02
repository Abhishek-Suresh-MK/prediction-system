import json
import os
from engine.spec_mapper import SpecMapper

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


class LaptopLoader:
    """
    Loads laptop data in 3 modes:
      - 'predefined': only laptops.json
      - 'custom':     only user-provided laptops
      - 'combined':   predefined + user-provided laptops

    All laptops store the processor as a 'cpu' string.
    cpu_score is always derived at load time by SpecMapper.map_cpu() —
    it is never read from a pre-stored number in any JSON file.
    """

    def __init__(self, laptops_path=None, criteria_path=None):
        self.laptops_path  = laptops_path  or os.path.join(_ROOT, "data",   "laptops.json")
        self.criteria_path = criteria_path or os.path.join(_ROOT, "config", "criteria.json")
        self.spec_mapper   = SpecMapper()

    def load_criteria(self):
        if not os.path.exists(self.criteria_path):
            raise FileNotFoundError(f"Criteria file not found: {self.criteria_path}")
        with open(self.criteria_path) as f:
            return json.load(f)

    def load_predefined_laptops(self):
        if not os.path.exists(self.laptops_path):
            raise FileNotFoundError(f"Laptops file not found: {self.laptops_path}")
        with open(self.laptops_path) as f:
            raw = json.load(f)
        return [self.spec_mapper.enrich_laptop(lap) for lap in raw]

    def validate_laptop(self, laptop_data):
        """Validate required fields for a custom laptop entry."""
        required = ["name", "price", "cpu", "gpu", "ram", "storage", "battery", "weight", "display"]
        for field in required:
            if field not in laptop_data or laptop_data[field] in [None, "", []]:
                raise ValueError(f"Missing required field: '{field}'")
        if float(laptop_data["price"]) <= 0:
            raise ValueError("Price must be a positive number.")
        if float(laptop_data["battery"]) <= 0:
            raise ValueError("Battery must be a positive number.")
        if float(laptop_data["weight"]) <= 0:
            raise ValueError("Weight must be a positive number.")
        return True

    def enrich_custom(self, laptop, index):
        """Validate, assign ID, cast numerics, then enrich via SpecMapper."""
        self.validate_laptop(laptop)
        laptop["id"]            = f"custom_{index}"
        laptop["category_tags"] = ["custom"]
        laptop["price"]         = float(laptop["price"])
        laptop["battery"]       = float(laptop["battery"])
        laptop["weight"]        = float(laptop["weight"])
        # 'cpu' is the processor name string — SpecMapper derives cpu_score from it
        return self.spec_mapper.enrich_laptop(laptop)

    def get_data(self, mode="combined", custom_laptops=None):
        """
        Returns (laptops_list, criteria_dict) for the given mode.
          'predefined' — built-in laptops only
          'custom'     — user-supplied laptops only
          'combined'   — built-in + user-supplied (default)
        """
        criteria       = self.load_criteria()
        custom_laptops = custom_laptops or []

        if mode == "predefined":
            laptops = self.load_predefined_laptops()

        elif mode == "custom":
            if not custom_laptops:
                raise ValueError("Custom mode requires at least one custom laptop.")
            laptops = [self.enrich_custom(lap, i + 1) for i, lap in enumerate(custom_laptops)]

        else:  # combined
            predefined      = self.load_predefined_laptops()
            enriched_custom = [self.enrich_custom(lap, i + 1) for i, lap in enumerate(custom_laptops)]
            laptops         = predefined + enriched_custom

        return laptops, criteria