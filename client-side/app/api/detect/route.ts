import { loadModel } from "@/lib/loadModel";
import { NextResponse } from "next/server";
import * as tf from "@tensorflow/tfjs-node";

export async function POST(request: Request) {
  try {
    const { image } = await request.json();

    if (!image) {
      return NextResponse.json(
        { message: "Image is required" },
        { status: 400 }
      );
    }

    const model = await loadModel();
    const imgTensor = tf.node.decodeImage(Buffer.from(image, "base64"));
    const predictions = await model.detect(imgTensor as tf.Tensor3D);

    return NextResponse.json({ predictions });
  } catch (error) {
    console.error("Error detecting objects:", error);
    return NextResponse.json(
      { message: "Error detecting objects" },
      { status: 500 }
    );
  }
}