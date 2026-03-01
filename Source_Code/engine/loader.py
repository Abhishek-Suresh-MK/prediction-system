import json
import os
from engine.spec_mapper import SpecMapper


class LaptopLoader:
    """
    Loads laptop data in 3 modes:
      - 'predefined': only laptops.json
      - 'custom':     only user-provided laptops
      - 'combined':   predefined + user-provided laptops
    """

    def __init__(self,
                 laptops_path="data/laptops.json",
                 criteria_path="config/criteria.json"):
        self.laptops_path = laptops_path
        self.criteria_path = criteria_path
        self.spec_mapper = SpecMapper()

    def load_criteria(self):
        if not os.path.exists(self.criteria_path):
            raise FileNotFoundError(f"Criteria file not found: {self.criteria_path}")
        with open(self.criteria_path, "r") as f:
            return json.load(f)

    def load_predefined_laptops(self):
        if not os.path.exists(self.laptops_path):
            raise FileNotFoundError(f"Laptops file not found: {self.laptops_path}")
        with open(self.laptops_path, "r") as f:
            raw = json.load(f)
        # Enrich each predefined laptop with mapped scores
        return [self.spec_mapper.enrich_laptop(lap) for lap in raw]

    def validate_laptop(self, laptop_data):
        """Validate required fields for a custom laptop."""
        required = ["name", "price", "cpu_score", "gpu", "ram", "storage", "battery", "weight", "display"]
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
        """Validate, assign ID, and enrich a custom laptop dict."""
        self.validate_laptop(laptop)
        laptop["id"] = f"custom_{index}"
        laptop["category_tags"] = ["custom"]
        laptop["price"] = float(laptop["price"])
        laptop["cpu_score"] = float(laptop["cpu_score"])
        laptop["battery"] = float(laptop["battery"])
        laptop["weight"] = float(laptop["weight"])
        return self.spec_mapper.enrich_laptop(laptop)

    def get_data(self, mode="combined", custom_laptops=None):
        """
        Returns (laptops_list, criteria_dict) based on mode.

        mode options:
          'predefined' - only built-in laptops
          'custom'     - only user-supplied laptops
          'combined'   - built-in + user-supplied
        """
        criteria = self.load_criteria()
        custom_laptops = custom_laptops or []

        if mode == "predefined":
            laptops = self.load_predefined_laptops()

        elif mode == "custom":
            if not custom_laptops:
                raise ValueError("Custom mode requires at least one custom laptop.")
            laptops = [self.enrich_custom(lap, i + 1) for i, lap in enumerate(custom_laptops)]

        else:  # combined (default)
            predefined = self.load_predefined_laptops()
            enriched_custom = [self.enrich_custom(lap, i + 1) for i, lap in enumerate(custom_laptops)]
            laptops = predefined + enriched_custom

        return laptops, criteria