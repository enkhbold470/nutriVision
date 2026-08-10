# Claude Integration Setup for NurtiVision

## Quick Start

**Yes, you can absolutely use Claude in your NurtiVision app!** I've integrated Claude's powerful vision and language capabilities into your food analysis system.

## What I've Added

### 1. **Smart Food Analysis** 🍎
- Upload food images → Claude identifies foods and estimates nutrition
- Detailed breakdown of calories, protein, carbs, fat, potassium, etc.
- Confidence ratings and portion size estimates

### 2. **AI-Powered Recommendations** 🧠
- Personalized nutrition advice based on your goals
- Smart meal suggestions
- Real-time warnings when approaching daily limits

### 3. **Conversational Chat Interface** 💬
- Ask Claude nutrition questions directly
- Get personalized advice based on your current intake
- Context-aware responses using your profile data

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Claude API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Get your API key from the dashboard

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your Claude API key:
# ANTHROPIC_API_KEY=your_api_key_here
```

### 4. Run the Backend
```bash
python app.py
```

## New API Endpoints

### 🍽️ Food Analysis
```
POST /api/analyze-food
Content-Type: multipart/form-data

Body: image file

Response:
{
  "foods_detected": [
    {
      "name": "Grilled Chicken Breast",
      "quantity": "6 oz",
      "calories": 231,
      "protein": 43.5,
      "carbs": 0,
      "fat": 5.0
    }
  ],
  "total_nutrition": {
    "calories": 231,
    "protein": 43.5,
    "carbs": 0,
    "fat": 5.0,
    "potassium": 256
  },
  "confidence": "high",
  "notes": "Well-cooked protein source"
}
```

### 🎯 Smart Recommendations
```
GET /api/get-recommendations?user_id=123

Response:
{
  "daily_calories": 1800,
  "ai_recommendations": [
    "Add more fiber-rich vegetables",
    "Consider a mid-afternoon protein snack"
  ],
  "meal_suggestions": [
    "Greek yogurt with berries",
    "Quinoa salad with chickpeas"
  ],
  "warnings": []
}
```

### 💬 Chat with Claude
```
POST /api/chat
Content-Type: application/json

Body:
{
  "message": "What should I eat for dinner?",
  "user_id": "123"
}

Response:
{
  "message": "Based on your current intake...",
  "user_context_included": true
}
```

## Benefits of Using Claude

### 🔥 **Advantages over OpenAI**
- **Better vision analysis**: More accurate food identification
- **Longer context**: Better understanding of complex meals
- **Safety-focused**: Built-in nutrition safety guidelines
- **Cost-effective**: Competitive pricing for vision tasks

### 🚀 **Perfect for NurtiVision**
- Real-time food analysis for VR/AR glasses
- Conversational interface for user questions
- Personalized recommendations based on goals
- Seamless integration with your existing database

## Next Steps

1. **Test the API**: Try uploading food images to `/api/analyze-food`
2. **Frontend Integration**: Connect your VR app to the new endpoints
3. **User Experience**: Add chat interface for nutrition questions
4. **Advanced Features**: 
   - Meal planning with Claude
   - Progress tracking insights
   - Smart notifications

Your NurtiVision app now has state-of-the-art AI capabilities! Claude will help make calorie tracking truly effortless for your users. 🎉