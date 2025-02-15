// app/page.tsx
'use client';
import { useState } from 'react';
import { Camera } from 'lucide-react';
import { NutritionInfo } from '../types/nutrition';

export default function Home() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [nutrition, setNutrition] = useState<NutritionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCapture = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload and analyze
    setIsLoading(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('/api/analyze-food', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setNutrition(data);
    } catch (error) {
      console.error('Error analyzing image:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Food Nutrition Analyzer
      </h1>

      <div className="space-y-8">
        {/* Camera Input */}
        <div className="flex justify-center">
          <label className="relative cursor-pointer">
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCapture}
              className="hidden"
            />
            <div className="h-16 w-16 bg-blue-500 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors">
              <Camera className="h-8 w-8 text-white" />
            </div>
          </label>
        </div>

        {/* Preview */}
        {imagePreview && (
          <div className="rounded-lg overflow-hidden shadow-lg">
            <img
              src={imagePreview}
              alt="Food preview"
              className="w-full object-cover max-h-[400px]"
            />
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center text-gray-600">
            Analyzing your food...
          </div>
        )}

        {/* Results */}
        {nutrition && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold">Nutrition Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-600">Total Calories</p>
                <p className="font-medium">{nutrition.totalCalories} kcal</p>
              </div>
              <div>
                <p className="text-gray-600">Potassium</p>
                <p className="font-medium">{nutrition.potassium} mg</p>
              </div>
              <div>
                <p className="text-gray-600">Protein</p>
                <p className="font-medium">{nutrition.protein} g</p>
              </div>
              <div>
                <p className="text-gray-600">Total Carbs</p>
                <p className="font-medium">{nutrition.totalCarbs} g</p>
              </div>
              <div>
                <p className="text-gray-600">Total Trans Fat</p>
                <p className="font-medium">{nutrition.totalTransFat} g</p>
              </div>
              <div>
                <p className="text-gray-600">Saturated Fat</p>
                <p className="font-medium">{nutrition.saturatedFat} g</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
