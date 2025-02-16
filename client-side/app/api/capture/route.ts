// app/api/capture/route.ts
import { NextResponse } from 'next/server';
import OpenAI from 'openai';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Ensure you have this in your .env file
});

export async function GET() {
  try {
    // Step 1: Fetch the image from localhost:5001/capture
    const captureResponse = await fetch('http://localhost:5001/capture');

    if (!captureResponse.ok) {
      throw new Error(`Failed to fetch image: ${captureResponse.statusText}`);
    }

    // Step 2: Get the image path from the response
    const { image_path } = await captureResponse.json();

    // Step 3: Fetch the actual image using the image_path
    const imageResponse = await fetch(`http://localhost:5001/${image_path}`);

    if (!imageResponse.ok) {
      throw new Error(`Failed to fetch image file: ${imageResponse.statusText}`);
    }

    // Step 4: Convert the image to Base64
    const imageBuffer = await imageResponse.arrayBuffer();
    const base64Image = Buffer.from(imageBuffer).toString('base64');

    // Step 5: Send the Base64 image to OpenAI
    const gptResponse = await openai.chat.completions.create({
      model: 'gpt-4o-mini', // Use the correct model name
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: 'What is in this image?',
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:image/jpeg;base64,${base64Image}`,
              },
            },
          ],
        },
      ],
      max_tokens: 300,
    });

    // Step 6: Log and return the GPT response
    console.log('GPT Response:', gptResponse.choices[0]);

    return NextResponse.json({
      // image_path,
      gpt_response: gptResponse.choices[0].message.content,
    });
  } catch (error) {
    console.error('Error in /api/capture:', error);
    return NextResponse.json(
      { message: 'Failed to process the image', error },
      { status: 500 }
    );
  }
}