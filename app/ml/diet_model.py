"""
diet_model.py — CP Decomposition Diet Model matching app (3).py.
Architecture: 
- Embeddings: User (100, rank=64), Food (586, rank=64), Context (179, rank=64)
- Projection: Nutrients (7) -> rank=64
- MLP: (rank * 3 + 3) -> 128 -> 64 -> 32 -> 1 (Sigmoid)
"""

import os
import torch
import torch.nn as nn
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "cp_diet_model.pth")
SCALER_PATH = os.path.join(BASE_DIR, "models", "nutrient_scaler.save")
GOAL_TO_ID_PATH = os.path.join(BASE_DIR, "models", "goal_to_id.save")
COUNTRY_TO_ID_PATH = os.path.join(BASE_DIR, "models", "country_to_id.save")
FOOD_TO_ID_PATH = os.path.join(BASE_DIR, "models", "food_to_id.save")

# Global variables to cache loaded objects
_model = None
_scaler = None
_goal_to_id = None
_country_to_id = None
_food_to_id = None

# SAMPLE_UIDS matching random_state=42 sample from numeric dataset
SAMPLE_UIDS = [84, 54, 71, 46, 45, 40, 23, 81, 11, 1]

# time_to_id mapping
_time_to_id = {"Breakfast": 1, "Lunch": 2, "Snack": 3, "Dinner": 4}
goal_display = {
    "Weight Gain": "Muscle Gain", 
    "Muscle Gain": "Muscle Gain",
    "Weight Loss": "Weight Loss", 
    "Maintenance": "Maintenance"
}

N_GOALS = 3
N_TIMES = 4


class CPDietModel(nn.Module):
    def __init__(self, n_users, n_foods, n_contexts, n_nutrients, rank=64):
        super().__init__()
        self.U = nn.Embedding(n_users    + 1, rank)
        self.F = nn.Embedding(n_foods    + 1, rank)
        self.C = nn.Embedding(n_contexts + 1, rank)
        for emb in [self.U, self.F, self.C]:
            nn.init.xavier_uniform_(emb.weight)
        self.emb_drop  = nn.Dropout(0.2)
        self.nut_proj  = nn.Linear(n_nutrients, rank)
        self.mlp = nn.Sequential(
             nn.Linear(rank * 3 + 3, 128),
             nn.BatchNorm1d(128),
             nn.ReLU(),
             nn.Dropout(0.3),
             nn.Linear(128, 64),
             nn.BatchNorm1d(64),
             nn.ReLU(),
             nn.Dropout(0.2),
             nn.Linear(64, 32),
             nn.ReLU(),
             nn.Linear(32, 1),
             nn.Sigmoid()
        )         
         
    def forward(self, u, f, ctx, nutrients):
        u_e   = self.emb_drop(self.U(u))
        f_e   = self.emb_drop(self.F(f))
        ctx_e = self.emb_drop(self.C(ctx))
        triple   = u_e * f_e * ctx_e
        n_e      = self.nut_proj(nutrients)
        nut_ctx  = n_e * ctx_e
        u_f      = u_e * f_e
        cp_score = triple.sum(dim=1,  keepdim=True)
        nc_score = nut_ctx.sum(dim=1, keepdim=True)
        uf_score = u_f.sum(dim=1,     keepdim=True)
        combined = torch.cat([triple, nut_ctx, u_f, cp_score, nc_score, uf_score], dim=1)
        return self.mlp(combined)


def encode_context(country_id, goal_id, time_id):
    return (int(country_id)-1)*(N_GOALS*N_TIMES) + (int(goal_id)-1)*N_TIMES + (int(time_id)-1)


def _load_model():
    """Lazily load the CP model and scaler artifacts."""
    global _model, _scaler, _goal_to_id, _country_to_id, _food_to_id
    if _model is not None:
        return

    _goal_to_id = joblib.load(GOAL_TO_ID_PATH)
    _country_to_id = joblib.load(COUNTRY_TO_ID_PATH)
    _food_to_id = joblib.load(FOOD_TO_ID_PATH)
    _scaler = joblib.load(SCALER_PATH)

    # Rebuild CP model (n_users=100, n_foods=586, n_contexts=179, n_nutrients=7)
    _model = CPDietModel(100, 586, 179, 7, rank=64)
    _model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    _model.eval()
    print("[DietModel] CPDietModel and artifacts loaded successfully.")


def compute_targets(weight: float, height: float, age: int, gender: str, goal: str) -> dict:
    """BMR computation matching original script Mifflin-St Jeor."""
    if gender.lower() == 'male':
        bmr = 10*weight + 6.25*height - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height - 5*age - 161

    if goal in ("Weight Gain", "Muscle Gain"):
        daily_cal, prot_factor = bmr + 500, 2.0
    elif goal == "Weight Loss":
        daily_cal, prot_factor = bmr - 500, 1.5
    else:
        daily_cal, prot_factor = bmr, 1.0

    return {
        "calories": max(1200, round(daily_cal)),
        "protein": round(weight * prot_factor)
    }


def score_food(food_name: str, food_data: dict, country_name: str, meal_type: str, user_id: int = 1, goal: str = "Maintenance") -> float:
    """Calculate average suitability score for a food item across SAMPLE_UIDS using CPDietModel."""
    _load_model()

    # Map food name to ID
    f_id = _food_to_id.get(food_name)
    if f_id is None:
        lower_food_map = {k.lower(): v for k, v in _food_to_id.items()}
        f_id = lower_food_map.get(food_name.lower(), 1)

    # Map country name to ID
    country_key = country_name.strip().title()
    country_id = _country_to_id.get(country_key)
    if country_id is None:
        lower_country_map = {k.lower(): v for k, v in _country_to_id.items()}
        country_id = lower_country_map.get(country_key.lower(), 1)

    # Map goal to ID
    dataset_goal = goal_display.get(goal, "Maintenance")
    goal_id = _goal_to_id.get(dataset_goal, 3)

    # Map meal type to ID
    t_id = _time_to_id.get(meal_type.strip().title(), 1)

    # Encode context ID
    ctx = encode_context(country_id, goal_id, t_id)

    # Compute nutritional features
    cals = float(food_data["calories"])
    prot = float(food_data["protein_g"])
    fat = float(food_data["fat_g"])
    carbs = float(food_data["carbs_g"])

    p_rat = prot / (cals + 1)
    c_rat = carbs / (cals + 1)
    f_rat = fat / (cals + 1)

    nut_features = pd.DataFrame(
        [[cals, prot, fat, carbs, p_rat, c_rat, f_rat]], 
        columns=['calories', 'protein_g', 'fat_g', 'carbs_g', 'protein_ratio', 'carb_ratio', 'fat_ratio']
    )
    scaled_nut = torch.FloatTensor(_scaler.transform(nut_features))

    # Evaluate model for all SAMPLE_UIDS
    scores = []
    with torch.no_grad():
        for uid in SAMPLE_UIDS:
            s = _model(
                torch.LongTensor([uid]),
                torch.LongTensor([f_id]),
                torch.LongTensor([ctx]),
                scaled_nut
            ).item()
            scores.append(s)

    return sum(scores) / len(scores)
