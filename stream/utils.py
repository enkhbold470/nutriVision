# calculate_bmr, calculate_daily_calories, calculate_daily_protein


def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation."""
    if gender.lower() == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_daily_calories(bmr, goal):
    """Calculate daily calorie needs based on goal."""
    # goal: 1 = lose weight, 2 = maintain, 3 = gain weight
    activity_factor = 1.375  # Assumes light activity
    maintenance = bmr * activity_factor
    
    if goal == 1:  # Lose weight
        return int(maintenance - 500)
    elif goal == 2:  # Maintain weight
        return int(maintenance)
    else:  # Gain weight
        return int(maintenance + 500)

def calculate_daily_protein(weight, goal):
    """Calculate daily protein needs in grams."""
    if goal == 1:  # Lose weight
        return int(weight * 2.2)  # 2.2g per kg of body weight
    elif goal == 2:  # Maintain weight
        return int(weight * 1.8)  # 1.8g per kg of body weight
    else:  # Gain weight
        return int(weight * 2.4)  # 2.4g per kg of body weight
