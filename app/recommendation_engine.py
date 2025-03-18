import json
import math
import os
from typing import Dict, List

config = {
    "budget_allocation": {
        "LIQUOR": 40,
        "WINE": 30,
        "BEER": 30
    },
    "head_allocation": {
        "LIQUOR": 40,
        "WINE": 30,
        "BEER": 30
    },
    "drink_per_type": {
        "LIQUOR": {
            "HEAVY": {"allocation": 100, "drinks_per_person": 4, "drink_size": 44.36},
            "MODERATE": {"allocation": 0, "drinks_per_person": 3, "drink_size": 44.36},
            "LIGHT": {"allocation": 0, "drinks_per_person": 2, "drink_size": 44.36}
        },
        "WINE": {
            "HEAVY": {"allocation": 100, "glasses_per_person": 4},
            "MODERATE": {"allocation": 0, "glasses_per_person": 3},
            "LIGHT": {"allocation": 0, "glasses_per_person": 2}
        },
        "BEER": {
            "HEAVY": {"allocation": 100, "bottles_per_person": 4},
            "MODERATE": {"allocation": 0, "bottles_per_person": 4},
            "LIGHT": {"allocation": 0, "bottles_per_person": 4}
        }
    },
    "bottle_size": 0.75
}



class RecommendationEngine:
    def __init__(self):
        print("started")
        self.bottle_size = config["bottle_size"]

    def calculate_total_drinks(self, number_of_attendees: int, per_person_budget: float,
                               categories: Dict[str, List[str]]):
        new_budget_allocation = self.recalculate_allocation_percentages(categories,
                                                                        config["budget_allocation"])
        new_head_allocation = self.recalculate_allocation_percentages(categories,
                                                                      config["head_allocation"])
        results: [] = []
        result: {} = {}
        for category, subcategories in categories.items():
            if category in config["drink_per_type"] and len(subcategories) > 0:
                if category == "LIQUOR":
                    result = self.calculate_spirit_quantity(number_of_attendees, per_person_budget, category,
                                                            subcategories, new_budget_allocation, new_head_allocation)
                elif category == "WINE":
                    result = self.calculate_wine_quantity(number_of_attendees, per_person_budget, category,
                                                          subcategories, new_budget_allocation, new_head_allocation)
                elif category == "BEER":
                    result = self.calculate_beer_quantity(number_of_attendees, per_person_budget, category,
                                                       subcategories, new_budget_allocation, new_head_allocation)
            if result:
                results.append(result)
        return {"data": results}

    def recalculate_allocation_percentages(self, categories, allocation_config):
        # Filter to only include categories that are in user's order
        available_categories = [cat for cat in allocation_config.keys() if cat in categories]

        if not available_categories:
            return {}

        # Get original percentages for available categories
        original_percentages = {cat: allocation_config[cat] for cat in available_categories}

        # Calculate sum of original percentages for available categories
        total_available_percentage = sum(original_percentages.values())

        # Redistribute to make it 100%
        new_percentages = {
            cat: (percentage / total_available_percentage) * 100
            for cat, percentage in original_percentages.items()
        }

        return new_percentages

    def calculate_spirit_quantity(self, number_of_attendees, per_person_budget, category, subcategories, new_budget_allocation, new_head_allocation):
        if new_budget_allocation[category] is not None:
            no_of_consumers = math.ceil(int(number_of_attendees) * (float(new_head_allocation[category] / 100)))
            budget_allocation = math.ceil(
                int(number_of_attendees) * float(per_person_budget) * (
                    float(new_budget_allocation[category] / 100)))
            total_litres_consumable = 0

            for data in config["drink_per_type"][category].values():
                if data["allocation"] > 0:
                    total_litres_consumable += (data["drinks_per_person"] * data[
                        "drink_size"] / 1000) * no_of_consumers * (
                                                       data["allocation"] / 100)

            bottles_needed = max(1, math.ceil(total_litres_consumable / self.bottle_size))
            per_bottle_cost = math.ceil(budget_allocation / bottles_needed)

        return self.allocate_subcategories(category, subcategories, bottles_needed, per_bottle_cost)

    def calculate_wine_quantity(self, number_of_attendees, per_person_budget, category, subcategories, new_budget_allocation, new_head_allocation):
        if new_budget_allocation[category] is not None:
            no_of_consumers = math.ceil(int(number_of_attendees) * (float(new_head_allocation[category] / 100)))
            budget_allocation = math.ceil(
                int(number_of_attendees) * float(per_person_budget) * (
                    float(new_budget_allocation[category] / 100)))
            total_glasses_consumable = 0

            for data in config["drink_per_type"][category].values():
                if data["allocation"] > 0:
                    total_glasses_consumable += data["glasses_per_person"] * no_of_consumers * (
                                data["allocation"] / 100)

            per_glass_cost = math.ceil(
                budget_allocation / total_glasses_consumable) if total_glasses_consumable > 0 else 0

        return self.allocate_subcategories(category, subcategories, total_glasses_consumable, per_glass_cost)

    def calculate_beer_quantity(self, number_of_attendees, per_person_budget, category, subcategories, new_budget_allocation, new_head_allocation):
        if new_budget_allocation[category] is not None:
            no_of_consumers = math.ceil(int(number_of_attendees) * (float(new_head_allocation[category] / 100)))
            budget_allocation = math.ceil(
                int(number_of_attendees) * float(per_person_budget) * (
                    float(new_budget_allocation[category] / 100)))
            total_bottles_consumable = 0

            for data in config["drink_per_type"][category].values():
                if data["allocation"] > 0:
                    total_bottles_consumable += math.ceil(
                        data["bottles_per_person"] * no_of_consumers * (data["allocation"] / 100))

            per_bottle_cost = math.ceil(
                budget_allocation / total_bottles_consumable) if total_bottles_consumable > 0 else 0

        return self.allocate_subcategories(category, subcategories, total_bottles_consumable, per_bottle_cost)

    def allocate_subcategories(self, category: dict, subcategories: dict, total_units: int, per_unit_cost: float):
        subcategory_distribution = {}
        subcategory_count = len(subcategories)
        unit_per_subcategory = max(1, math.ceil(total_units / subcategory_count))
        remaining_units = total_units

        for subcategory in subcategories:
            if remaining_units == 0:
                break
            elif remaining_units == 1:
                subcategory_distribution[subcategory] = 1
                remaining_units -= 1
            else:
                subcategory_distribution[subcategory] = min(unit_per_subcategory, remaining_units)
                remaining_units -= unit_per_subcategory

        return {
            "category": category,
            "total_units": int(total_units),
            "per_unit_cost": per_unit_cost,
            "subcategories": subcategory_distribution
        }

    def recommend_products(self, number_of_attendees, per_person_budget, user_input_categories):
        results = self.calculate_total_drinks(number_of_attendees, per_person_budget, user_input_categories)
        return json.dumps(results, indent=4)

# if __name__ == '__main__':
#     engine = RecommendationEngineTest()
#     drinks = {
#         "LIQUOR": ["WHISKEY", "VODKA"],
#         "BEER": ["IPA", "LAGER"]
#     }
#     print(engine.calculate_total_drinks(50, 20, drinks))

