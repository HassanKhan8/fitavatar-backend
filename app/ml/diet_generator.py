"""
diet_generator.py — Meal plan generator using CPDietModel suitability scoring.
"""

from app.ml.food_database import get_foods, get_country_key
from app.ml.diet_model import score_food

MEAL_CAL_RATIOS  = {"breakfast": 0.25, "lunch": 0.35, "snack": 0.10, "dinner": 0.30}
MEAL_PROT_RATIOS = {"breakfast": 0.25, "lunch": 0.35, "snack": 0.05, "dinner": 0.35}
CAL_WEIGHTS      = [0.38, 0.35, 0.27]


def _calc_option(items: list, cal_target: float, prot_target: float, option_idx: int) -> dict:
    """
    Calculate portion sizes (grams) for each item in the option.
    Uses BMR targets and caloric/protein densities.
    """
    if len(items) < 3:
        return {"option": option_idx, "foods": []}

    food_list = []
    for idx, item in enumerate(items[:3]):
        gcal  = (cal_target  * CAL_WEIGHTS[idx] / item['cal_100'])  * 100
        gprot = (prot_target * CAL_WEIGHTS[idx] / item['prot_100']) * 100 \
                if item['prot_100'] > 0 else gcal
        
        # Portion size capped between 30g and 400g (as per app (3).py)
        g  = max(min(round((gcal + gprot) / 2), 400), 30)
        pr = round((item['prot_100'] * g) / 100)
        cl = round((item['cal_100']  * g) / 100)

        food_list.append({
            "name":       item['name'],
            "grams":      g,
            "protein":    pr,
            "calories":   cl,
            "score":      round(item['score'], 3),
            "protein_g":  item['prot_100'],
            "calories_per_100g": item['cal_100'],
        })

    return {"option": option_idx, "foods": food_list}


def generate_meal_plan(
    location: str,
    target_calories: int,
    target_protein: int,
    user_id: int,
    goal: str = "Maintenance",
) -> dict:
    """
    Generate a full-day meal plan for the given country, targets and user goal.
    Scores candidates with CPDietModel and pools them into high, medium, and low protein buckets.
    """
    country_key = get_country_key(location)
    meals_out   = {}

    for meal_type in ["breakfast", "lunch", "snack", "dinner"]:
        foods = get_foods(location, meal_type)

        if not foods:
            meals_out[meal_type] = []
            continue

        cal_target  = target_calories * MEAL_CAL_RATIOS[meal_type]
        prot_target = target_protein * MEAL_PROT_RATIOS[meal_type]

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
                    goal         = goal,
                )
            except Exception:
                score = 0.5    # fallback if model errors
            
            scored.append({
                "name":      food["name"],
                "score":     score,
                "cal_100":   food["calories"],
                "prot_100":  food["protein_g"],
                "fat_100":   food["fat_g"],
                "carbs_100": food["carbs_g"],
            })

        # Pool selection logic from app (3).py
        high = sorted([x for x in scored if x['prot_100'] >= 15], key=lambda x: x['score'], reverse=True)
        med  = sorted([x for x in scored if  5 <= x['prot_100'] < 15], key=lambda x: x['score'], reverse=True)
        low  = sorted([x for x in scored if x['prot_100'] <  5], key=lambda x: x['score'], reverse=True)
        all_ = sorted(scored, key=lambda x: x['score'], reverse=True)

        def build_pool(exclude):
            pool, used = [], set(exclude)
            for bucket in [high, med, low, all_]:
                for item in bucket:
                    if item['name'] not in used:
                        pool.append(item)
                        used.add(item['name'])
                        break
                if len(pool) == 3:
                    break
            for item in all_:
                if len(pool) >= 3:
                    break
                if item['name'] not in {i['name'] for i in pool}:
                    pool.append(item)
            return pool

        pool1 = build_pool(set())
        pool2 = build_pool({i['name'] for i in pool1})

        opt1 = _calc_option(pool1, cal_target, prot_target, option_idx=1)
        opt2 = _calc_option(pool2, cal_target, prot_target, option_idx=2)

        meals_out[meal_type.title()] = [opt1, opt2]

    return meals_out
