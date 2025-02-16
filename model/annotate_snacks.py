from groundingdino.util.inference import load_model, load_image, predict, annotate
import os
import torch
import matplotlib.pyplot as plt
from datasets import load_dataset
from tqdm import tqdm
from PIL import Image

def run_dino(dino, image, text_prompt='food', box_threshold=0.4, text_threshold=0.1):
    boxes, logits, phrases = predict(
        model = dino, 
        image = image, 
        caption = text_prompt, 
        box_threshold = box_threshold, 
        text_threshold = text_threshold,
        device = 'cuda',
    )
    return boxes, logits, phrases

dino = load_model('./GroundingDINO_SwinT_OGC.cfg.py', './groundingdino_swint_ogc.pth')

# image_source, image = load_image('dog.jpeg')
# boxes, logits, phrases = run_dino(dino, image, text_prompt='dog')

# annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
# plt.imshow(annotated_frame)
# plt.show()

snacks_data = '../snacks'

def dino_annotate(dino, data, data_size, data_dir, curr=0):
    image_dir = f'{data_dir}/images'
    label_dir = f'{data_dir}/labels'
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)
    
    count = curr
    for i in tqdm(range(data_size)):
        image_path = f'{image_dir}/image{count}.jpg'
        label_path = f'{label_dir}/image{count}.txt'   

        image = Image.open(f'{data[i]}.jpg')
        image = image.resize((640, 640))
        image.save(image_path)
        
        _, image = load_image(image_path)
        boxes, _, _ = run_dino(dino, image, text_prompt='food')
        # annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
        label = ['0 ' + ' '.join(list(map(str, b))) for b in boxes.tolist()]
        label = '\n'.join(label)
        # plt.imsave(os.path.join(f'{data_dir}/images', f'image{i}.jpg'), annotated_frame)
        with open(label_path, 'w') as f:
            f.write(label)
        
        count += 1

train_images = []
for dir in os.listdir(f'{snacks_data}/train'):
    if not os.path.isdir(f'{snacks_data}/train/{dir}'):
        continue
    for file in os.listdir(f'{snacks_data}/train/{dir}'):
        train_images.append(f'{snacks_data}/train/{dir}/{file.split(".")[0]}')

for dir in os.listdir(f'{snacks_data}/val'):
    if not os.path.isdir(f'{snacks_data}/train/{dir}'):
        continue
    for file in os.listdir(f'{snacks_data}/val/{dir}'):
        train_images.append(f'{snacks_data}/val/{dir}/{file.split(".")[0]}')

val_images = []
for dir in os.listdir(f'{snacks_data}/test'):
    if not os.path.isdir(f'{snacks_data}/train/{dir}'):
        continue
    for file in os.listdir(f'{snacks_data}/test/{dir}'):
        val_images.append(f'{snacks_data}/test/{dir}/{file.split(".")[0]}')

curr_train = 10000
curr_val = 3000

dino_annotate(dino, train_images, len(train_images) - 1, './data/train', curr_train)
dino_annotate(dino, val_images, len(val_images) - 1, './data/val', curr_val)

# config = {
#     'names': ['food'],
#     'nc': 1,
#     'train': 'train/images',
#     'val': 'valid/images'
# }

# with open('data/data.yaml', 'w') as f:
#     yaml.dump(config, f)
