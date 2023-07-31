"""Converts the walaris COCO format dataset to work with this repository by 
doing the following:

1. Changes image ids to ensure that they are integers (some of the image ids in 
the current walaris coco format datasets are very large numbers. So large that
they cannot be stored as a numpy long or integer and must be stored as a numpy
object, which gives a nasty compatibility bug that took HOURS to find.)

2. Modifies the relative paths of the images to be the absolute path to that
image (so you do not have to move all of the images to a different folder.)

3. Ensures that every annotation has an 'iscrowd' value set to 0.

4. Ensure that every annotation has an 'area' value
"""

import json
import os
from tqdm import tqdm
import random

def convert_dataset(train_json_file: str, 
                    val_json_file: str,
                    dataset_name: str):
    """See above description."""

    # save the new json file in the ./datasets folder in the coco standard
    # directory structure
    annotations_path = os.path.join('datasets', dataset_name, 'annotations')
    if not os.path.exists(annotations_path):
        os.makedirs(annotations_path)

    img_count = 1
    ann_count = 1

    ######################### Create Train Json File ##########################

    print('Loading file...')
    with open(train_json_file, 'r') as file:
        data = json.load(file)

    images = data['images']
    annotations = data['annotations']

    # go through each image and map the image id to a new image id
    old2new_img_id = dict()

    print('Creating img_id dictionary...')
    for img_dict in images:
        old_img_id = img_dict['id']
        new_img_id = img_count
        old2new_img_id[old_img_id] = new_img_id
        img_count += 1

    base_img_path = os.path.join(os.environ.get('WALARIS_MAIN_DATA_PATH'),
                                 'Images')
    
    # loop through every image and:
    # 1. change the old image id to the new img id
    # 2. change the file_name to the full path of the image

    for idx in tqdm(range(len(images))):
        old_img_id = images[idx]['id']
        new_img_id = old2new_img_id[old_img_id]

        relative_file_path = images[idx]['file_name']
        full_file_path = os.path.join(base_img_path,
                                      relative_file_path)
        
        # change the values for the image
        images[idx]['id'] = new_img_id
        images[idx]['file_name'] = full_file_path

    # loop through every annotation and:
    # 1. convert old img id to new img id
    # 2. provide a new annotation id, starting from 0
    
    for idx in tqdm(range(len(annotations))):
        old_img_id = annotations[idx]['image_id']
        new_img_id = old2new_img_id[old_img_id]
        new_ann_id = ann_count
        bbox = annotations[idx]['bbox']
        

        # change the values for the annotation
        annotations[idx]['image_id'] = new_img_id
        annotations[idx]['id'] = new_ann_id
        annotations[idx]['area'] = bbox[2] * bbox[3]
        annotations[idx]['iscrowd'] = 0
        ann_count += 1

    # save the new file
    data['images'] = images
    data['annotations'] = annotations

    new_train_json_path = os.path.join(annotations_path,
                                   'instances_train.json')

    print('Saving file...')
    with open(new_train_json_path, 'w') as file:
        json.dump(data, file)
    
    ######################### Create Val Json File ############################

    print('Loading_file...')
    with open(val_json_file, 'r') as file:
        data = json.load(file)

    images = data['images']
    annotations = data['annotations']

    # go through each image and map the image id to a new image id
    old2new_img_id = dict()

    print('Creating img_id dict...')
    for img_dict in images:
        old_img_id = img_dict['id']
        new_img_id = img_count
        old2new_img_id[old_img_id] = new_img_id
        img_count += 1

    base_img_path = os.path.join(os.environ.get('WALARIS_MAIN_DATA_PATH'),
                                 'Images')
    
    # loop through every image and:
    # 1. change the old image id to the new img id
    # 2. change the file_name to the full path of the image

    for idx in tqdm(range(len(images))):
        old_img_id = images[idx]['id']
        new_img_id = old2new_img_id[old_img_id]

        relative_file_path = images[idx]['file_name']
        full_file_path = os.path.join(base_img_path,
                                      relative_file_path)
        
        # change the values for the image
        images[idx]['id'] = new_img_id
        images[idx]['file_name'] = full_file_path

    # loop through every annotation and:
    # 1. convert old img id to new img id
    # 2. provide a new annotation id, starting from 0
    
    for idx in tqdm(range(len(annotations))):
        old_img_id = annotations[idx]['image_id']
        new_img_id = old2new_img_id[old_img_id]
        new_ann_id = ann_count
        bbox = annotations[idx]['bbox']

        # change the values for the annotation
        annotations[idx]['image_id'] = new_img_id
        annotations[idx]['id'] = new_ann_id
        annotations[idx]['area'] = bbox[2] * bbox[3]
        annotations[idx]['iscrowd'] = 0
        ann_count += 1
    
    # save the new file
    data['images'] = images
    data['annotations'] = annotations

    print('Saving file...')
    new_train_json_path = os.path.join(annotations_path,
                                   'instances_val.json')

    with open(new_train_json_path, 'w') as file:
        json.dump(data, file)

def get_test_dataset(base_json_file):
    with open(base_json_file, 'r') as file:
        data = json.load(file)

    images = data['images']
    annotations = data['annotations']

    # go through each image and map the image id to a new image id
    old2new_img_id = dict()

    print('Creating img_id dict...')
    img_count = 1
    for img_dict in images:
        old_img_id = img_dict['id']
        new_img_id = img_count
        old2new_img_id[old_img_id] = new_img_id
        img_count += 1

    img_ids_to_add = set()
    num_samples = 100
    count = 0
    while count < num_samples:

        img_dict = random.choice(images)
        img_id = img_dict['id']
        if img_id in img_ids_to_add:
            continue
        img_ids_to_add.add(img_id)
        count += 1
    
    ann_count = 1
    new_annotations = []
    for idx, annotation in enumerate(annotations):
        img_id = annotation['image_id']
        if img_id not in img_ids_to_add:
            continue
            
        new_img_id = old2new_img_id[img_id]
        bbox = annotation['bbox']

        annotation['area'] = bbox[2] * bbox[3]
        annotation['image_id'] = new_img_id
        annotation['iscrowd'] = 0
        annotation['id'] = ann_count
        new_annotations.append(annotation)
        ann_count += 1
    
    new_images = []
    for idx, image in enumerate(images):
        img_id = image['id']
        if img_id not in img_ids_to_add:
            continue
        
        new_img_id = old2new_img_id[img_id]

        image['id'] = new_img_id
        new_images.append(image)

    data['images'] = new_images
    data['annotations'] = new_annotations

    with open('test_train.json', 'w') as file:
        json.dump(data, file)

if __name__=='__main__':

    original_train_json_path = '/home/grayson/Documents/model_training/Tarsier_Main_Dataset/Labels_NEW/day/train_COCO/exp3_dino_fully_labelled_day_train.json'
    original_val_json_path = '/home/grayson/Documents/model_training/Tarsier_Main_Dataset/Labels_NEW/day/val_COCO/exp1_dino_fully_labelled_day_val_results.json'
    dataset_name = 'exp3_train'

    # convert_dataset(original_train_json_path,
    #                 original_val_json_path,
    #                 dataset_name)

    get_test_dataset(original_train_json_path)
    

