// app/api/analyze-food/route.ts
import { NextResponse } from 'next/server';
import { FoodItem} from '@/app/types/nutrition';
import { OpenAI } from 'openai';
import sharp from 'sharp';


const system_message = `You are a nutritionist and software engineer, you only respond with json with nutrition output 
{
        "name": "string",
        "nutrition": {
            "total_cal": number,
            "potassium": number,
            "protein": number,
            "total_carbs": number,
            "total_fat": number
        }
    }`;

// Initialize OpenAI client
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});



async function encodeImage(imageBuffer: Buffer): Promise<string> {
  return imageBuffer.toString('base64');
}

async function calculateNutrition(imageBuffer: Buffer): Promise<FoodItem> {
  try {
    // Convert image to base64
    const base64Image = await encodeImage(imageBuffer);
    
    // Call OpenAI API
    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
            role: "system",
            content: system_message 
        },  
        {
          role: "user",
          content: [
            { type: "text", text: "Please identify the food respond with json" },
            {
              type: "image_url",
              image_url: { url: `data:image/jpeg;base64,${base64Image}` },
            },
          ],
        }
      ],
    });

    // Process nutrition data from USDA API
    const API_KEY = process.env.USDA_API_KEY;
    const content = completion?.choices[0]?.message?.content || "null";
    // Extract JSON from markdown code fences
    const jsonString = content.startsWith("```json") ? content.slice(7, -3) : content;
    console.log("Extracted JSON String:", jsonString);
    const foodData = JSON.parse(jsonString);
    console.log("Parsed Food Data:", foodData);

    // Map foodData to NutritionInfo
    const foodNutrition: FoodItem = {
        name: foodData.name || "Unknown",
        nutrition: {
            total_cal: foodData.nutrition.total_cal || 0,
            potassium: foodData.nutrition.potassium || 0,
            protein: foodData.nutrition.protein || 0,
            total_carbs: foodData.nutrition.total_carbs || 0,
            total_fat: foodData.nutrition.total_fat || 0,
        }
    };

    // just return all json data
    return foodNutrition;
  } catch (error) {
    console.error('Error in calculateNutrition:', error);
    throw error;
  }
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const image = formData.get('image') as File;
    
    if (!image) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Convert image to buffer
    const bytes = await image.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Process the image and get nutrition information
    const nutritionInfo = await calculateNutrition(buffer);

    return NextResponse.json(nutritionInfo);
  } catch (error) {
    console.error('Error processing image:', error);
    return NextResponse.json(
      { error: 'Failed to process image' },
      { status: 500 }
    );
  }
}