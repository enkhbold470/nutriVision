"use client"

import { useRef, useState, useEffect } from "react"
import { ObjectDetector, FilesetResolver } from "@mediapipe/tasks-vision"

export default function Camera() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [objectDetector, setObjectDetector] = useState<ObjectDetector | null>(null)
  const [isDetecting, setIsDetecting] = useState(false)
  const [nutritionInfo, setNutritionInfo] = useState({
    calories: 0,
    potassium: 0,
    protein: 0,
    carbs: 0,
    transFat: 0,
    satFat: 0,
  })

  // Initialize MediaPipe Object Detector
  useEffect(() => {
    const initializeDetector = async () => {
      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
      )
      const detector = await ObjectDetector.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite",
          delegate: "GPU"
        },
        scoreThreshold: 0.5,
        maxResults: 5
      })
      setObjectDetector(detector)
    }
    initializeDetector()
  }, [])

  // Setup camera
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

  // Object detection loop
  const detectObjects = async () => {
    if (!objectDetector || !videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const detectFrame = async () => {
      if (!isDetecting) return

      // Draw current video frame on canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // Detect objects
      const detections = await objectDetector.detect(canvas)
      
      // Draw detection boxes
      detections.detections.forEach(detection => {
        const box = detection.boundingBox
        ctx.strokeStyle = "#00FF00"
        ctx.lineWidth = 2
        ctx.strokeRect(
          box.originX,
          box.originY,
          box.width,
          box.height
        )
        
        // Draw label
        ctx.fillStyle = "#00FF00"
        ctx.fillText(
          `${detection.categories[0].categoryName} ${Math.round(detection.categories[0].score * 100)}%`,
          box.originX,
          box.originY - 5
        )
      })

      requestAnimationFrame(detectFrame)
    }

    setIsDetecting(true)
    detectFrame()
  }

  const stopDetection = () => {
    setIsDetecting(false)
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 text-green-600">Food Scanner</h1>
      <div className="mb-4 relative">
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          className="w-full h-64 object-cover rounded-lg" 
        />
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-64 object-cover rounded-lg"
        />
      </div>
      <button
        onClick={isDetecting ? stopDetection : detectObjects}
        className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 mb-4"
      >
        {isDetecting ? 'Stop Detection' : 'Start Detection'}
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

