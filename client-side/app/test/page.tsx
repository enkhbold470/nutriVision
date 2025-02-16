"use client";
import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";

export default function Home() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCapture = async () => {
    setLoading(true);
    console.log("Capture started...");

    try {
      const response = await fetch('/api/capture');
      console.log("Response received:", response);
      console.log("Response status:", response.status);
      console.log("Response headers:", response.headers);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log("Data received:", data);
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
      console.log("Capture completed.");
    }
  };

  return (
    <div>
      <h1>NutriVision</h1>
      <Button onClick={handleCapture} disabled={loading}>
        {loading ? "Processing..." : "Capture and Analyze Food"}
      </Button>
      {result && <p>Result: {JSON.stringify(result)}</p>}
    </div>
  );
}