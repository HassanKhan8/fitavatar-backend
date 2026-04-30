"""
diet_model.py — Real DietTensorModel matching notebook code.ipynb
Architecture: 
- embeddings: user (20), food (20), country (10), time (10) 
- fc: 64 -> 128 -> 64 -> 32 -> 1 (Sigmoid)
- dynamically loads food_to_id from categorical.csv to guarantee 0-error offset.
"""

import os
import torch
import torch.nn as nn
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "diet_recommender_weights.pth")
SCALER_PATH = os.path.join(BASE_DIR, "models", "nutrient_scaler.save")
DATA_DIR = os.path.join(BASE_DIR, "data")
CAT_DATA_PATH = os.path.join(DATA_DIR, "diet_data_categorical.csv")

# ── Dynamic Mappings from Training Data ───────────────────────────────────────
# These maps are exclusively initialized when _load_model is called.
_food_to_id: dict = {}
_country_to_id: dict = {}
_time_to_id: dict = {"Breakfast": 1, "Lunch": 2, "Snack": 3, "Dinner": 4}

_model = None
_scaler = None

class DietTensorModel(nn.Module):
    def __init__(self, n_users, n_foods, n_countries, n_times):
        super().__init__()
        self.user_embed    = nn.Embedding(n_users + 1, 20)
        self.food_embed    = nn.Embedding(n_foods + 1, 20)
        self.country_embed = nn.Embedding(n_countries + 1, 10)
        self.time_embed    = nn.Embedding(n_times + 1, 10)
        self.fc = nn.Sequential(
            nn.Linear(64, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 32),  nn.ReLU(),
            nn.Linear(32, 1),   nn.Sigmoid(),
        )
        
    def forward(self, u, f, c, t, nutrients):
        x = torch.cat([self.user_embed(u), self.food_embed(f),
                       self.country_embed(c), self.time_embed(t), nutrients], dim=1)
        return self.fc(x)

def _load_model():
    """Lazily load the model, scaler, and exact dataset mappings."""
    global _model, _scaler, _food_to_id, _country_to_id
    
    if _model is not None:
        return

    # 1. Rebuild EXACT alphabetical mappings from notebook's categorical data
    df_cat = pd.read_csv(CAT_DATA_PATH)
    unique_countries = sorted(df_cat['country'].unique())
    unique_foods = sorted(df_cat['food_name'].unique())

    _country_to_id = {name: i+1 for i, name in enumerate(unique_countries)}
    _food_to_id = {name: i+1 for i, name in enumerate(unique_foods)}
    
    # 2. Hardcoded limits from the training (Numeric CSV max indices)
    # The training notebook extracted n_foods from max string ID mappings OR max df_num.
    # From df_num: n_users=100, n_foods=586, n_countries=15, n_times=4
    _model = DietTensorModel(n_users=100, n_foods=586, n_countries=15, n_times=4)

    if os.path.exists(MODEL_PATH):
        _model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu", weights_only=True))
        print("[DietModel] Loaded DietTensorModel weights successfully.")
    else:
        print("[DietModel] ERR: weights file not found!")
        
    _model.eval()

    if os.path.exists(SCALER_PATH):
        _scaler = joblib.load(SCALER_PATH)
        print("[DietModel] Loaded nutrient scaler successfully.")
    else:
        print("[DietModel] ERR: scaler not found!")

def compute_targets(weight: float, height: float, age: int, gender: str, goal: str) -> dict:
    """Mifflin-St Jeor BMR + goal adjustment. Exact match to code.ipynb."""
    if gender.lower() == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    goal_l = goal.lower()
    if "gain" in goal_l:
        daily_cal = bmr + 500
        prot_factor = 2.0
    elif "loss" in goal_l:
        daily_cal = bmr - 500
        prot_factor = 1.5
    else:
        daily_cal = bmr
        prot_factor = 1.0

    return {
        "calories": max(1200, int(daily_cal)), 
        "protein": int(weight * prot_factor)
    }

def score_food(food_name: str, food_data: dict, country_name: str, meal_type: str, user_id: int = 1) -> float:
    """Return model suitability score 0-1 for a food item given context."""
    _load_model()
    
    # Map cleanly
    f_id = _food_to_id.get(food_name, 1)
    c_id = _country_to_id.get(country_name, 15)
    t_id = _time_to_id.get(meal_type.title(), 1)
    
    raw = [[
        float(food_data["calories"]), 
        float(food_data["protein_g"]),
        float(food_data["fat_g"]),    
        float(food_data["carbs_g"])
    ]]

    if _scaler is not None:
        nut_input = torch.FloatTensor(_scaler.transform(np.array(raw, dtype=np.float32)))
    else:
        nut_input = torch.FloatTensor(raw)

    with torch.no_grad():
        score = _model(
            torch.LongTensor([user_id]), 
            torch.LongTensor([f_id]),
            torch.LongTensor([c_id]), 
            torch.LongTensor([t_id]), 
            nut_input
        ).item()
        
    return float(score)
