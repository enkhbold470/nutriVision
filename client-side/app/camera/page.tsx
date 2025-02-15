"use client"

import { useRef, useState, useEffect } from "react"

export default function Camera() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [nutritionInfo, setNutritionInfo] = useState({
    calories: 0,
    potassium: 0,
    protein: 0,
    carbs: 0,
    transFat: 0,
    satFat: 0,
  })

  useEffect(() => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream
          }
        })
        .catch((error) => console.error("Error accessing the camera:", error))
    }
  }, [])

  // This function would typically be called when an image is captured and analyzed
  const updateNutritionInfo = () => {
    // In a real app, this would be replaced with actual image analysis and data retrieval
    setNutritionInfo({
      calories: Math.floor(Math.random() * 500),
      potassium: Math.floor(Math.random() * 1000),
      protein: Math.floor(Math.random() * 50),
      carbs: Math.floor(Math.random() * 100),
      transFat: Math.floor(Math.random() * 5),
      satFat: Math.floor(Math.random() * 10),
    })
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 text-green-600">Food Scanner</h1>
      <div className="mb-4">
        <video ref={videoRef} autoPlay playsInline className="w-full h-64 object-cover rounded-lg" />
      </div>
      <button
        onClick={updateNutritionInfo}
        className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 mb-4"
      >
        Scan Food
      </button>
      <div className="bg-gray-100 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-2">Nutrition Information</h2>
        <ul className="space-y-2">
          <li>Total Calories: {nutritionInfo.calories} kcal</li>
          <li>Potassium: {nutritionInfo.potassium} mg</li>
          <li>Protein: {nutritionInfo.protein} g</li>
          <li>Total Carbs: {nutritionInfo.carbs} g</li>
          <li>Total Trans Fat: {nutritionInfo.transFat} g</li>
          <li>Saturated Fat: {nutritionInfo.satFat} g</li>
        </ul>
      </div>
    </div>
  )
}

