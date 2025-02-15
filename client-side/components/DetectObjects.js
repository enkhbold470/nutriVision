"use client";
import { useState } from 'react';

export default function DetectObjects() {
  const [predictions, setPredictions] = useState([]);
  const [image, setImage] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const img = new Image();
        img.src = e.target.result;
        img.onload = async () => {
          setImage(img);
          const canvas = document.createElement('canvas');
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0);
          const imageData = ctx.getImageData(0, 0, img.width, img.height);

          const response = await fetch('/api/detect', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
          });

          const data = await response.json();
          setPredictions(data.predictions);
        };
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleImageUpload} />
      {image && <img src={image.src} alt="Uploaded" />}
      <div>
        <h3>Predictions:</h3>
        <ul>
          {predictions.map((prediction, index) => (
            <li key={index}>
              {prediction.class} - {Math.round(prediction.score * 100)}%
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}