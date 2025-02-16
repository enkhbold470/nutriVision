
from backend import db
from backend.db import User
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
# change

def calculate_caloric_deficit(goal_weight_loss, target_date):
    """Calculate required daily caloric deficit based on goal weight loss and timeline."""
    today = datetime.today()
    target_date = datetime.strptime(target_date, "%Y-%m-%d")  # Convert string to date
    days_to_target = (target_date - today).days

    if days_to_target <= 0:
        return None, "Target date must be in the future."

    # Convert lbs to kg
    weight_loss_kg = goal_weight_loss * 0.453592  
    calorie_deficit_needed = weight_loss_kg * 7700  # 1 kg ≈ 7700 kcal
    daily_deficit = calorie_deficit_needed / days_to_target

    return round(daily_deficit, 2), None




@app.route("/" , methods=['GET'])
def home():
        return "Hello World"

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({'error': 'No image provided'}), 400

        # TODO: Implement AI food recognition and nutrition analysis
        # Placeholder response
        nutrition_data = {
            'food_name': 'Sample Food',
            'calories': 250,
            'protein': 10,
            'carbs': 30,
            'fat': 8
        }
        return jsonify(nutrition_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/track-meal', methods=['POST'])
def track_meal():
    try:
        data = request.get_json()
        # TODO: Implement meal tracking logic with database
        return jsonify({'message': 'Meal tracked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-recommendations', methods=['GET'])
def get_recommendations():
    try:
        user_id = request.args.get('user_id')
        # TODO: Implement personalized recommendations
        recommendations = {
            'daily_calories': 2000,
            'suggestions': [
                'Increase protein intake',
                'Add more vegetables to your diet',
                'Stay hydrated'
            ]
        }
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-if-healthy', methods=['GET'])
def isGoalHealthy():
    try:
        goal_weight_loss = float(request.args.get('goal'))  # Weight loss in lbs
        target_date = request.args.get('targetDate')  # Target date (YYYY-MM-DD)

        # Calculate daily caloric deficit needed
        daily_deficit, error = calculate_caloric_deficit(goal_weight_loss, target_date)

        if error:
            return jsonify({'error': error}), 400

        # Convert daily deficit to weekly weight loss
        weekly_loss = (daily_deficit * 7) / 3500  # Convert kcal to lbs
        is_healthy = 0.5 <= weekly_loss <= 2  # Healthy range: 0.5–2 lbs per week

        if is_healthy is True:
            return jsonify({
                'goal_weight_loss': goal_weight_loss,
                'weekly_weight_loss': round(weekly_loss, 2),
                'is_healthy_goal': 'This is a healthy goal.'
            })
        else:
            return jsonify({
                'goal_weight_loss': goal_weight_loss,
                'weekly_weight_loss': round(weekly_loss, 2),
                'is_healthy_goal': 'This is not a healthy goal.'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#fitness calculator
@app.route('/api/track-progress', methods=['GET'])
def track_progress():
        if User.calories <= User.max_daily_calories:
            status = None
        else:
            status = "Not reaching goal."

        return jsonify({
            'status': status
        })

#display nutrients
@app.route('/api/display-nutrients', methods=['GET'])
def return_nutrients():
        return jsonify({
            'calories': User.calories,
            'potassium': User.potassium,
            'protein': User.protein,
            'carbs': User.carbs,
            'totalfat': User.totalfat
        })

#display calories
@app.route('/api/calories', methods=['GET'])
def return_nutrients():
        return jsonify({
            'calories': User.calories,
        })



    
#you've exceeded the intake of fat/cholestoral for today. 
#take the food data from the open ai. increment values for calories, fat, and carbs. if they reach a max value, then return a message saying that they've exceeded the intake of that nutrient, to the frontend. 

# Define daily intake limits (can be adjusted per dietary guidelines)
#a method that defines user's daily limits based on their goal weight, and their goal date:
def daily_limits(user):
    """
    Calculate daily calorie and protein intake limits based on user's goal weight and target date.
    
    Returns:
        - daily_calories (int): The daily calorie limit needed to achieve the goal.
        - daily_protein (int): The recommended daily protein intake in grams.
    """
    try:
        # Convert targetDate from datetime object
        today = datetime.today()
        days_remaining = (user.targetDate - today).days

        if days_remaining <= 0:
            return None, None  # Target date must be in the future

        # Convert goal weight loss to kg
        weight_loss_kg = user.goal * 0.453592  # 1 lb = 0.453592 kg

        # Calculate required daily caloric deficit
        total_calorie_deficit = weight_loss_kg * 7700  # 1 kg ≈ 7700 kcal
        daily_caloric_deficit = total_calorie_deficit / days_remaining

        # Calculate BMR (Mifflin-St Jeor Equation)
        height_cm = user.height * 2.54  # Convert inches to cm
        weight_kg = user.weight * 0.453592  # Convert lbs to kg

        if user.gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * user.age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * user.age - 161

        # Calculate daily caloric limit (maintenance calories - deficit)
        daily_calories = max(1200, int(bmr - daily_caloric_deficit))  # Ensures it doesn't drop too low

        # Calculate daily protein intake (1.5g per kg of target weight)
        target_weight_kg = weight_kg - weight_loss_kg
        daily_protein = max(50, int(target_weight_kg * 1.5))  # Ensures minimum protein intake

        user.max_daily_calories = daily_calories
        user.max_daily_protein = daily_protein

        db.session.commit()

    except Exception as e:
        print(f"Error in daily_limits: {str(e)}")
        return None, None



@app.route("/api/recieveNutrientData", methods=['POST'])
def recieveNutrientData():
    try:
        data = request.get_json()
        user_id = data.get('user_id')  # User ID to update in database
        nutrient_mapping = data.get('nutrient_mapping')

        if not user_id or not nutrient_mapping:
            return jsonify({'error': 'Missing user_id or nutrient_mapping'}), 400

        # Aggregate the sum of each nutrient
        aggregated_nutrients = {
            "calories": sum(filter(None, nutrient_mapping.get("Calories", []))),
            "potassium": sum(filter(None, nutrient_mapping.get("Potassium, K", []))),
            "protein": sum(filter(None, nutrient_mapping.get("protein", []))),
            "carbs": sum(filter(None, nutrient_mapping.get("Carbohydrate, by difference", []))),
            "totalfat": sum(filter(None, nutrient_mapping.get("Total lipid (fat)", []))),
        }

        # Fetch user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user's daily intake
        user.calories += aggregated_nutrients["calories"]
        user.potassium += aggregated_nutrients["potassium"]
        user.protein += aggregated_nutrients["protein"]
        user.carbs += aggregated_nutrients["carbs"]
        user.totalfat += aggregated_nutrients["totalfat"]

        # Commit changes to the database
        db.session.commit()

        # Check for exceeded limits
        if user.calories > user.max_daily_calories:
            # Construct response
            response = {
            "updated_nutrients": {
                "calories": user.calories,
                "potassium": user.potassium,
                "protein": user.protein,
                "carbs": user.carbs,
                "totalfat": user.totalfat,
            },
            "notification": "You've exceeded the intake of calories for today. Please adjust your meals accordingly.",
        }
        else:
            response = {
            "updated_nutrients": {
                "calories": user.calories,
                "potassium": user.potassium,
                "protein": user.protein,
                "carbs": user.carbs,
                "totalfat": user.totalfat,
            },
            "notification": None
        }
            
        
        return jsonify(response), 200

            

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    





if __name__ == '__main__':
    app.run(debug=True)
