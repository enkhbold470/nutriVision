import anthropic
import base64
import json
import os
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

class ClaudeFoodAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
    
    def encode_image(self, image_file):
        """Convert image file to base64 string for Claude API"""
        try:
            # Open and process the image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (Claude has size limits)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Encode to base64
            return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error encoding image: {str(e)}")
    
    def analyze_food_image(self, image_file):
        """Analyze food image and return nutritional information"""
        try:
            # Encode the image
            base64_image = self.encode_image(image_file)
            
            # Create the prompt for food analysis
            prompt = """
            Please analyze this food image and provide detailed nutritional information. 
            
            I need you to identify:
            1. What food items are visible in the image
            2. Estimate the portion sizes/quantities
            3. Calculate nutritional information per item and total
            
            Please respond ONLY with a valid JSON object in this exact format:
            {
                "foods_detected": [
                    {
                        "name": "food name",
                        "quantity": "estimated portion size",
                        "calories": number,
                        "protein": number,
                        "carbs": number,
                        "fat": number,
                        "fiber": number,
                        "sodium": number,
                        "potassium": number
                    }
                ],
                "total_nutrition": {
                    "calories": total_calories,
                    "protein": total_protein,
                    "carbs": total_carbs,
                    "fat": total_fat,
                    "fiber": total_fiber,
                    "sodium": total_sodium,
                    "potassium": total_potassium
                },
                "confidence": "high/medium/low",
                "notes": "any relevant observations about the food or portion sizes"
            }
            
            Please ensure all numeric values are numbers (not strings), and be as accurate as possible with your estimates.
            """
            
            # Make the API call to Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse the response
            response_text = message.content[0].text
            
            # Try to parse JSON from the response
            try:
                nutrition_data = json.loads(response_text)
                return nutrition_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    nutrition_data = json.loads(json_match.group())
                    return nutrition_data
                else:
                    raise Exception("Could not parse nutrition data from Claude response")
                    
        except Exception as e:
            raise Exception(f"Error analyzing food with Claude: {str(e)}")
    
    def get_food_recommendations(self, user_goals, current_nutrition):
        """Get personalized food recommendations based on user goals and current intake"""
        try:
            prompt = f"""
            Based on the following user information, provide personalized nutrition recommendations:
            
            User Goals: {user_goals}
            Current Daily Nutrition: {current_nutrition}
            
            Please provide recommendations in JSON format:
            {{
                "recommendations": [
                    "specific recommendation 1",
                    "specific recommendation 2",
                    "specific recommendation 3"
                ],
                "meal_suggestions": [
                    "healthy meal suggestion 1",
                    "healthy meal suggestion 2"
                ],
                "warnings": [
                    "any warnings about current intake"
                ]
            }}
            """
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                recommendations = json.loads(response_text)
                return recommendations
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    recommendations = json.loads(json_match.group())
                    return recommendations
                else:
                    raise Exception("Could not parse recommendations from Claude response")
                    
        except Exception as e:
            raise Exception(f"Error getting recommendations from Claude: {str(e)}")