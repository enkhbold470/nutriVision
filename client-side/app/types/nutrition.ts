// app/types/nutrition.ts
export interface FoodItem {
  name: string;
  nutrition: NutritionInfo;
}
export interface NutritionInfo {
  total_cal: number;
  potassium: number;
  protein: number;
  total_carbs: number;
  total_fat: number;
}
