'use client';
import { useState, useRef } from 'react';
import { Camera } from 'lucide-react';
import { FoodItem } from '../types/nutrition';

export default function Home() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [nutrition, setNutrition] = useState<FoodItem | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleCapture = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Create preview from file input
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload and analyze image file
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

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsCameraActive(true);
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0);
      const dataURL = canvas.toDataURL('image/png');
      setImagePreview(dataURL);
      // Stop the camera
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      setIsCameraActive(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Food Nutrition Analyzer
      </h1>

      <div className="space-y-8">
        {/* Camera or File Input Section */}
        <div className="flex justify-center space-x-4">
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
          <button
            onClick={startCamera}
            className="h-16 w-32 bg-green-500 text-white rounded-full flex items-center justify-center hover:bg-green-600 transition-colors"
          >
            Start Camera
          </button>
        </div>

        {/* Video Stream & Capture Button */}
        {isCameraActive && (
          <div className="flex flex-col items-center space-y-4">
            <video ref={videoRef} className="rounded-lg shadow-lg max-h-[400px]" />
            <button
              onClick={capturePhoto}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Take Photo
            </button>
          </div>
        )}

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
            <h3 className="text-lg font-medium">{nutrition.name}</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-600">Total Calories</p>
                <p className="font-medium">{nutrition.nutrition.total_cal} kcal</p>
              </div>
              <div>
                <p className="text-gray-600">Potassium</p>
                <p className="font-medium">{nutrition.nutrition.potassium} mg</p>
              </div>
              <div>
                <p className="text-gray-600">Protein</p>
                <p className="font-medium">{nutrition.nutrition.protein} g</p>
              </div>
              <div>
                <p className="text-gray-600">Total Carbs</p>
                <p className="font-medium">{nutrition.nutrition.total_carbs} g</p>
              </div>
              <div>
                <p className="text-gray-600">Total Fat</p>
                <p className="font-medium">{nutrition.nutrition.total_fat} g</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}