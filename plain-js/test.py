# import onnx

# model = onnx.load("yolo11n_food.onnx")
# metadata = model.metadata_props

# for prop in metadata:
#     print(f"{prop.key}: {prop.value}")c

import onnxruntime as ort
import numpy as np
from PIL import Image
import cv2

session = ort.InferenceSession("yolo11n_food.onnx")

image = Image.open('food.jpeg').resize((640, 640))
image = np.array(image).astype(np.float32)[:, :, :3]
og_image = image
image = image.transpose(2, 0, 1) / 255.0
image = image[np.newaxis, ...]

def video():
    cap = cv2.VideoCapture(1)

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 640))
        og_frame = frame
        frame = frame[:, :, :3]
        frame = frame.astype(np.float32) / 255.0
        frame = frame.transpose(2, 0, 1)
        frame = frame[np.newaxis, ...]

        # results = model(frame)
        outputs = session.run(None, {"images": image})
        outputs = np.array(outputs)
        outputs = outputs.transpose(0, 1, 3, 2)
        outputs = outputs.flatten()

        boxes = []
        scores = []
        classes = []

        skip = 5
        for i in range(0, len(outputs), skip):
            xc = int(outputs[i])
            yc = int(outputs[i + 1])
            w = int(outputs[i + 2])
            h = int(outputs[i + 3])
            conf = outputs[i + 4]
            cl = 'food'  # assuming single class "food"

            # print(xc, yc, w, h, conf, cl)

            if conf > 0.5:
                boxes.append([xc - w // 2, yc - h // 2, xc + w // 2, yc + h // 2])
                scores.append(conf)
                classes.append(cl)

        boxes = np.array(boxes)
        scores = np.array(scores)

        for box, score in zip(boxes, scores):
            x1, y1, x2, y2 = box
            cv2.rectangle(og_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{cl} {score:.2f}"
            cv2.putText(og_frame, label, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # im.save(f'frame_{i}.jpg')
        cv2.imshow('frame', og_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# img = np.random.rand(1, 3, 640, 640).astype(np.float32)  # Example normalized input
# print(image.shape)

outputs = session.run(None, {"images": image})
outputs = np.array(outputs)
outputs = outputs.transpose(0, 1, 3, 2)
outputs = outputs.flatten()

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

coco_classes = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", 
    "boat", "traffic light", "fire hydrant", "N/A", "stop sign", "parking meter", 
    "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", 
    "zebra", "giraffe", "N/A", "backpack", "umbrella", "N/A", "handbag", "tie", 
    "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", 
    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "N/A", 
    "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", 
    "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", 
    "potted plant", "bed", "N/A", "dining table", "toilet", "N/A", "tv", "laptop", 
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", 
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", 
    "toothbrush"
]

our_classes = ["food"]

def non_maximum_suppression(boxes, scores, iou_threshold=0.5):
    # Sort the boxes by their score (confidence)
    indices = np.argsort(scores)[::-1]  # Sort in descending order

    selected_boxes = []
    selected_scores = []
    
    while len(indices) > 0:
        i = indices[0]  # Take the box with the highest score
        selected_boxes.append(boxes[i])
        selected_scores.append(scores[i])

        remaining_indices = []
        for j in indices[1:]:
            # Calculate IoU (Intersection over Union) between the current box and the rest
            iou = compute_iou(boxes[i], boxes[j])
            if iou < iou_threshold:
                remaining_indices.append(j)

        # Update indices to only include those boxes that haven't been suppressed
        indices = remaining_indices

    return np.array(selected_boxes), np.array(selected_scores)

def compute_iou(box1, box2):
    x1, y1, x2, y2 = box1
    xx1, yy1, xx2, yy2 = box2

    # Compute intersection
    inter_x1 = max(x1, xx1)
    inter_y1 = max(y1, yy1)
    inter_x2 = min(x2, xx2)
    inter_y2 = min(y2, yy2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    # Compute union
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (xx2 - xx1) * (yy2 - yy1)
    
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0

def test_nms(og_image=og_image, outputs=outputs):
    # Now integrate NMS into your existing code
    boxes = []
    scores = []
    classes = []

    skip = 5
    og_image = og_image.astype(np.uint8)

    for i in range(0, len(outputs), skip):
        x1 = int(outputs[i])
        y1 = int(outputs[i + 1])
        x2 = int(outputs[i + 2])
        y2 = int(outputs[i + 3])
        conf = outputs[i + 4]
        cl = our_classes[0]  # assuming single class "food"

        if conf > 0.5:
            boxes.append([x1, y1, x2, y2])
            scores.append(conf)
            classes.append(cl)

    # Perform NMS
    boxes = np.array(boxes)
    scores = np.array(scores)

    # Apply NMS (IoU threshold can be adjusted)
    filtered_boxes, filtered_scores = non_maximum_suppression(boxes, scores, iou_threshold=0.5)

    # Annotate image with the remaining boxes
    for box, score in zip(filtered_boxes, filtered_scores):
        x1, y1, x2, y2 = box
        cv2.rectangle(og_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{cl} {score:.2f}"
        cv2.putText(og_image, label, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save the annotated image
    image = Image.fromarray(og_image)
    image.save('food_annotated_nms.jpg')

test_nms(og_image=og_image, outputs=outputs)

# skip = 5
# og_image = og_image.astype(np.uint8)
# for i in range(0, len(outputs), skip):
#     x1 = int(outputs[i])   # Ensure integer values
#     y1 = int(outputs[i + 1])
#     x2 = int(outputs[i + 2])
#     y2 = int(outputs[i + 3])
#     # confs = outputs[i + 4: i + skip]
#     # conf = np.max(confs)
#     # cl = coco_classes[np.argmax(confs)]

#     conf = outputs[i + 4]
#     cl = our_classes[0]

#     # print(x1, y1, x2, y2, conf, cl)

#     if conf > 0.5:
#         print(x1, y1, x2, y2, conf, cl)
#         cv2.rectangle(og_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         label = f"{cl} {conf:.2f}"
#         cv2.putText(og_image, label, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# image = Image.fromarray(og_image)
# image.save('burrito_annotated.jpg')
