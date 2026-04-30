"""
bmi.py — BMI calculation and category classification.
NOTE: The original bmi.py file had incorrect content (was a duplicate
of diet_model.py). This is the correct implementation.
"""


def bmi_profile(weight: float, height: float) -> dict:
    """
    Calculate BMI and return category.

    Args:
        weight: Weight in kilograms
        height: Height in centimeters

    Returns:
        {"bmi": float, "category": str, "advice": str}
    """
    if height <= 0 or weight <= 0:
        return {"bmi": 0.0, "category": "Unknown", "advice": "Invalid measurements."}

    height_m = height / 100.0
    bmi = round(weight / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        advice   = "Consider a calorie surplus plan to reach a healthy weight."
    elif bmi < 25.0:
        category = "Normal"
        advice   = "Great! Maintain your current healthy lifestyle."
    elif bmi < 30.0:
        category = "Overweight"
        advice   = "A calorie deficit diet and regular exercise can help."
    else:
        category = "Obese"
        advice   = "Consult a healthcare professional for a structured plan."

    return {
        "bmi":      bmi,
        "category": category,
        "advice":   advice,
    }
