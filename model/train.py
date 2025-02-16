import yaml

config = {
    'names': ['food'],
    'nc': 1,
    'train': '/global/cfs/projectdirs/m3641/Akaash/yolov8/data/train',
    'val': '/global/cfs/projectdirs/m3641/Akaash/yolov8/data/val'
}

with open('data/data.yaml', 'w') as f:
    yaml.dump(config, f)

from ultralytics import YOLO

model = YOLO('yolo11n.pt')
model.train(data='data/data.yaml', epochs=10, device='cuda')
model.save('yolo11n_food_2.pt')
