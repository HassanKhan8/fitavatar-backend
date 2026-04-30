"""
diet_generator.py — Meal plan generator matching notebook output exactly.

Output format (matches screenshot):
  - breakfast: 25% of daily_cal → 2 options × 3 foods, each food shown with grams + protein + kcal
  - lunch:     35%
  - snack:     10%
  - dinner:    30%

Food selection: model scores all country foods for the meal, top-3 = Option 1, next-3 = Option 2.
Grams: target_cal_per_item / food_cal_per_100g × 100, capped at 300g.
"""
import random
from app.ml.food_database import get_foods, get_country_key
from app.ml.diet_model import score_food

MEAL_RATIOS = {"breakfast": 0.25, "lunch": 0.35, "snack": 0.10, "dinner": 0.30}
OPTIONS_PER_MEAL = 2
FOODS_PER_OPTION = 3


def _build_option(ranked_foods: list, option_idx: int, daily_cal: int, ratio: float) -> dict:
    """
    Build one meal option from a ranked food slice.
    Returns option dict matching API response shape.
    """
    slice_start = option_idx * FOODS_PER_OPTION
    slice_end   = slice_start + FOODS_PER_OPTION
    items       = ranked_foods[slice_start:slice_end]

    if not items:
        return {"option": option_idx + 1, "foods": []}

    target_cal_per_item = (daily_cal * ratio) / FOODS_PER_OPTION
    food_list = []

    for food in items:
        cal_per_100g  = max(food["calories"], 1)
        grams         = (target_cal_per_item / cal_per_100g) * 100
        grams         = min(round(grams), 300)   # cap at 300g (matches notebook)

        achieved_cal  = round((food["calories"]  * grams) / 100)
        achieved_prot = round((food["protein_g"] * grams) / 100)

        food_list.append({
            "name":       food["name"],
            "grams":      grams,
            "protein":    achieved_prot,
            "calories":   achieved_cal,
            "protein_g":  food["protein_g"],   # per-100g reference
            "calories_per_100g": food["calories"],
        })

    return {"option": option_idx + 1, "foods": food_list}


def generate_meal_plan(
    location: str,
    target_calories: int,
    target_protein: int,
    user_id: int,
) -> dict:
    """
    Generate a full-day meal plan for the given country and targets.
    Uses DietTensorModel to rank foods by suitability before selection.
    Returns dict with keys: breakfast, lunch, snack, dinner.
    Each value is a list of option dicts.
    """
    country_key = get_country_key(location)
    meals_out   = {}

    for meal_type, ratio in MEAL_RATIOS.items():
        foods = get_foods(location, meal_type)

        if not foods:
            meals_out[meal_type] = []
            continue

        # Score every food item with the AI model
        scored = []
        for food in foods:
            try:
                score = score_food(
                    food_name    = food["name"],
                    food_data    = food,
                    country_name = country_key,
                    meal_type    = meal_type,
                    user_id      = user_id,
                )
            except Exception:
                score = 0.5    # fallback if model errors
            scored.append((score, food))

        # Sort descending by model score
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [f for _, f in scored]

        # Build OPTIONS_PER_MEAL options, each with FOODS_PER_OPTION items
        options = []
        for i in range(OPTIONS_PER_MEAL):
            opt = _build_option(ranked, i, target_calories, ratio)
            options.append(opt)

        meals_out[meal_type] = options

    return meals_out
