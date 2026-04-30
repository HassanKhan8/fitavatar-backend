"""
food_database.py — Dynamic Food Database
Loads diet_data_categorical.csv and serves food data per country/meal.
Countries are exactly those in the CSV (15 total):
  Brazil, China, France, Greece, India, Italy, Japan, Lebanon,
  Mexico, Pakistan, Saudi Arabia, Spain, Thailand, Turkey, USA
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAT_DATA_PATH = os.path.join(BASE_DIR, "data", "diet_data_categorical.csv")

# Exact 15 countries present in the training dataset
SUPPORTED_COUNTRIES = [
    "Brazil", "China", "France", "Greece", "India", "Italy",
    "Japan", "Lebanon", "Mexico", "Pakistan", "Saudi Arabia",
    "Spain", "Thailand", "Turkey", "USA",
]

_df_cat = None


def _load_data():
    global _df_cat
    if _df_cat is None:
        if not os.path.exists(CAT_DATA_PATH):
            raise FileNotFoundError(f"Missing dataset: {CAT_DATA_PATH}")
        _df_cat = pd.read_csv(CAT_DATA_PATH)


def get_supported_countries() -> list:
    """Return the 15 supported country names (matches training CSV)."""
    return SUPPORTED_COUNTRIES


def get_country_key(location: str) -> str:
    """
    Normalise user-supplied location string to match CSV country name.
    Falls back to 'Pakistan' if country not in supported list.
    """
    # title-case match first
    title = location.strip().title()
    if title in SUPPORTED_COUNTRIES:
        return title
    # case-insensitive fallback
    lower_map = {c.lower(): c for c in SUPPORTED_COUNTRIES}
    return lower_map.get(location.strip().lower(), "Pakistan")


def get_foods(country_name: str, meal_type: str) -> list:
    """
    Returns unique food dicts for a specific country + meal type.
    meal_type must match the CSV 'time_of_day' value (title-cased):
      Breakfast | Lunch | Snack | Dinner
    """
    _load_data()

    c_name = get_country_key(country_name)
    m_name = meal_type.strip().title()

    filtered = _df_cat[
        (_df_cat["country"] == c_name) &
        (_df_cat["time_of_day"] == m_name)
    ]

    unique = filtered.drop_duplicates(subset=["food_name"])

    return [
        {
            "name":       row["food_name"],
            "calories":   float(row["calories"]),
            "protein_g":  float(row["protein_g"]),
            "fat_g":      float(row["fat_g"]),
            "carbs_g":    float(row["carbs_g"]),
        }
        for _, row in unique.iterrows()
    ]
