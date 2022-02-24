import os.path
import random
import copy

import json
import argparse

import numpy as np
import datetime as dt

import xmlConv #JetsonXMLHandler()

parser = argparse.ArgumentParser(description='User args')
parser.add_argument('--dataset_dir', required=True, help='Path to dataset annotations')
parser.add_argument('--test_percentage', type=int, default=10, required=False, help='Percentage of images used for the testing set')
parser.add_argument('--val_percentage', type=int, default=10, required=False, help='Percentage of images used for the validation set')
parser.add_argument('--nr_trials', type=int, default=10, required=False, help='Number of splits')
parser.add_argument('--convert', type=str, default='no', required=False, help='Convert to another trainable annotations')

args = parser.parse_args()

ann_input_path = args.dataset_dir + '/' + 'annotations.json'

# Load annotations
with open(ann_input_path, 'r') as f:
    dataset = json.loads(f.read())

#anns = dataset['annotations']
scene_anns = dataset['scene_annotations']
#imgs = dataset['images']

#nr_images = len(imgs)

#nr_testing_images = int(nr_images*args.test_percentage*0.01+0.5)
#nr_nontraining_images = int(nr_images*(args.test_percentage+args.val_percentage)*0.01+0.5)

# Internal Rename
theBatch = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
for x in dataset['images']:
    splited = x['file_name'].split('/')
    theBatchNum = int((splited[0]).replace('batch_',''))
    theBatch[theBatchNum].append(splited[1])
    
for x in theBatch:
    x.sort()

countUp = 0 #Join all batch from batch_0/000000.JPG
batchIndex = 0
for nImages in theBatch:
    for nImage in nImages:
        for image in dataset['images']: #Dirty way to find, or maybe the best idk
            if image['file_name'] == "batch_"+str(batchIndex)+'/'+nImage:
                strCU = str(countUp)
                countUp+=1
                reName = ""
                for y in range(0,6-len(strCU)):
                    reName += "0"
                reName += strCU+".jpg"
                image['file_name'] = reName
                break
    batchIndex += 1

# The real split dataset
picked_cat = ["Other plastic bottle", "Clear plastic bottle", "Disposable plastic cup", 
              "Disposable food container", "Other plastic container"]
categ_id = []

categ = {'images': [],
        'annotations': [],
        'categories': [],
        }

for split_cat in dataset['categories']:
    if split_cat['name'] in picked_cat:
        categ['categories'].append(split_cat)
        categ_id.append(split_cat['id'])
for split_cat in dataset['annotations']:
    if split_cat['category_id'] in categ_id:
        categ['annotations'].append(split_cat)
for split_cat in dataset['images']:
    for split_img in categ['annotations']:
        if split_img['image_id'] == split_cat['id']:
            categ['images'].append(split_cat)

anns = categ['annotations']
imgs = categ['images']
nr_images = len(imgs)

nr_testing_images = int(nr_images*args.test_percentage*0.01+0.5)
nr_nontraining_images = int(nr_images*(args.test_percentage+args.val_percentage)*0.01+0.5)
for i in range(args.nr_trials):
    random.shuffle(imgs)
    
    # Add new datasets
    train_set = {
        'info': None,
        'images': [],
        'annotations': [],
        'scene_annotations': [],
        'licenses': [],
        'categories': [],
        'scene_categories': [],
    }
    train_set['info'] =  dataset['info']
    #train_set['categories'] = dataset['categories']
    train_set['categories'] = categ['categories']
    train_set['scene_categories'] = dataset['scene_categories']

    val_set = copy.deepcopy(train_set)
    test_set = copy.deepcopy(train_set)

    test_set['images'] = imgs[0:nr_testing_images]
    val_set['images'] = imgs[nr_testing_images:nr_nontraining_images]
    train_set['images'] = imgs[nr_nontraining_images:nr_images]

    # Aux Image Ids to split annotations
    test_img_ids, val_img_ids, train_img_ids = [],[],[]
    for img in test_set['images']:
        test_img_ids.append(img['id'])

    for img in val_set['images']:
        val_img_ids.append(img['id'])

    for img in train_set['images']:
        train_img_ids.append(img['id'])

    # Split instance annotations
    for ann in anns:
        if ann['image_id'] in test_img_ids:
            test_set['annotations'].append(ann)
        elif ann['image_id'] in val_img_ids:
            val_set['annotations'].append(ann)
        elif ann['image_id'] in train_img_ids:
            train_set['annotations'].append(ann)

    # Split scene tags
    for ann in scene_anns:
        if ann['image_id'] in test_img_ids:
            test_set['scene_annotations'].append(ann)
        elif ann['image_id'] in val_img_ids:
            val_set['scene_annotations'].append(ann)
        elif ann['image_id'] in train_img_ids:
            train_set['scene_annotations'].append(ann)

    # Write dataset splits
    ann_train_out_path = args.dataset_dir + '/' + 'annotations_' + str(i) +'_train.json'
    ann_val_out_path   = args.dataset_dir + '/' + 'annotations_' + str(i) + '_val.json'
    ann_test_out_path  = args.dataset_dir + '/' + 'annotations_' + str(i) + '_test.json'

    if args.convert == "no":
        print('writing...')
        with open(ann_train_out_path, 'w+') as f:
            f.write(json.dumps(train_set))

        with open(ann_val_out_path, 'w+') as f:
            f.write(json.dumps(val_set))

        with open(ann_test_out_path, 'w+') as f:
            f.write(json.dumps(test_set))
            
    elif args.convert == "voc":
        print('converting...')
        for image in train_set['images']:
            converter = JetsonXMLHandler()
            converter.changeName(image["file_name"])
            converter.changeSize(str(image["width"]),str(image["height"]))
            for annotate in train_set['annotations']:
                if annotate['image_id'] == image['id']:
                    rawbbox = annotate['bbox']
                    bbox = (rawbbox[0],
                            rawbbox[1],
                            rawbbox[0]+rawbbox[2],
                            rawbbox[1]+rawbbox[3])

                    for label in val_set['categories']:
                        if label['id'] == annotate['category_id']:
                            Label = label['name']
                    converter.createObject(Label, bbox)
            converter.writeXML('train')
        
        for image in val_set['images']:
            converter = JetsonXMLHandler()
            converter.changeName(image["file_name"])
            converter.changeSize(str(image["width"]),str(image["height"]))
            for annotate in val_set['annotations']:
                if annotate['image_id'] == image['id']:
                    rawbbox = annotate['bbox']
                    bbox = (rawbbox[0],
                            rawbbox[1],
                            rawbbox[0]+rawbbox[2],
                            rawbbox[1]+rawbbox[3])
                    for label in val_set['categories']:
                        if label['id'] == annotate['category_id']:
                            Label = label['name']
                    converter.createObject(Label, bbox)
            converter.writeXML('val')

        for image in test_set['images']:
            converter = JetsonXMLHandler()
            converter.changeName(image["file_name"])
            converter.changeSize(str(image["width"]),str(image["height"]))
            for annotate in test_set['annotations']:
                if annotate['image_id'] == image['id']:
                    rawbbox = annotate['bbox']
                    for label in val_set['categories']:
                        if label['id'] == annotate['category_id']:
                            Label = label['name']
                    bbox = (rawbbox[0],
                            rawbbox[1],
                            rawbbox[0]+rawbbox[2],
                            rawbbox[1]+rawbbox[3])
                    converter.createObject(Label, bbox)
            converter.writeXML('test')  
            
        print('We just do it once for voc')
        break
print('Done') 
