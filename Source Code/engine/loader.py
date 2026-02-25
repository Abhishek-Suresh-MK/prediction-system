import json
import os

class LaptopLoader:
    def __init__(self, laptops_path="data/laptops.json", criteria_path="config/criteria.json"):
        self.laptops_path = laptops_path
        self.criteria_path = criteria_path

    def load_criteria(self):
        """Load criteria configuration (cost/beneficial)."""
        if not os.path.exists(self.criteria_path):
            raise FileNotFoundError(f"Criteria file not found at: {self.criteria_path}")

        with open(self.criteria_path, "r") as f:
            return json.load(f)

    def load_predefined_laptops(self):
        """Load predefined laptops from JSON."""
        if not os.path.exists(self.laptops_path):
            raise FileNotFoundError(f"Laptops file not found at: {self.laptops_path}")

        with open(self.laptops_path, "r") as f:
            return json.load(f)

    def validate_laptop(self, laptop_data, criteria):
        """
        Validate laptop contains required fields and numeric values.
        """
        required_fields = ["name"] + list(criteria.keys())

        for field in required_fields:
            if field not in laptop_data:
                raise ValueError(f"Missing required field: {field}")

            if field != "name":
                if not isinstance(laptop_data[field], (int, float)):
                    raise ValueError(f"Field '{field}' must be numeric.")
                if laptop_data[field] < 0:
                    raise ValueError(f"Field '{field}' cannot be negative.")
        return True

    def get_combined_data(self, custom_laptop=None):
        """
        Returns merged dataset of predefined laptops and optional user laptop.
        """
        laptops = self.load_predefined_laptops()
        criteria = self.load_criteria()

        if custom_laptop:
            self.validate_laptop(custom_laptop, criteria)
            # Assign a simple ID based on current list length
            custom_laptop["id"] = len(laptops) + 1
            laptops.append(custom_laptop)

        return laptops, criteria
