"use client"; // Mark as a Client Component

import { useEffect, useRef, useState } from "react";

export default function WebcamDetect() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [predictions, setPredictions] = useState<any[]>([]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Error accessing webcam:", error);
      }
    };

    const detectObjects = async () => {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext("2d");

        if (context) {
          // Draw video frame on canvas
          context.drawImage(video, 0, 0, canvas.width, canvas.height);

          // Convert canvas image to base64
          const imageData = canvas.toDataURL("image/jpeg").split(",")[1];

          // Send image to API for detection
          const response = await fetch("/api/detect", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: imageData }),
          });

          const { predictions } = await response.json();
          setPredictions(predictions);

          // Draw bounding boxes on canvas
          predictions.forEach((pred: any) => {
            const [x, y, width, height] = pred.bbox;
            context.strokeStyle = "#FF0000";
            context.lineWidth = 2;
            context.strokeRect(x, y, width, height);
            context.fillStyle = "#FF0000";
            context.fillText(
              `${pred.class} (${Math.round(pred.score * 100)}%)`,
              x,
              y > 10 ? y - 5 : 10
            );
          });
        }
      }
    };

    startWebcam().then(() => {
      interval = setInterval(detectObjects, 100); // Detect objects every 100ms
    });

    return () => {
      clearInterval(interval);
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <div>
      <video ref={videoRef} autoPlay muted playsInline width={640} height={480} />
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        style={{ position: "absolute", top: 0, left: 0 }}
      />
      <div>
        <h3>Predictions:</h3>
        <ul>
          {predictions.map((pred, index) => (
            <li key={index}>
              {pred.class} - {Math.round(pred.score * 100)}%
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
