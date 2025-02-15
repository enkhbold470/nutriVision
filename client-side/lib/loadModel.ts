import * as cocoSsd from "@tensorflow-models/coco-ssd";

let model: cocoSsd.ObjectDetection | null = null;

export async function loadModel() {
  if (!model) {
    model = await cocoSsd.load();
  }
  return model;
}

