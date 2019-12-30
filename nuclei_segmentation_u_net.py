# -*- coding: utf-8 -*-
"""Nuclei_Segmentation_U_Net.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CtXzrycRwnunXffZWKPWMaVq4ybdJ7bO
"""

import os
import sys
import random
import warnings
import numpy as np
import pandas as pd

from tqdm import tqdm
from itertools import chain

from skimage.io import imread, imshow, imread_collection, concatenate_images
from skimage.transform import resize
from skimage.morphology import label

from keras.models import Model, load_model
from keras.layers import Input
from keras.layers.core import Dropout, Lambda
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D
from keras.layers.merge import Concatenate
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as k

import tensorflow as tf

import matplotlib.pyplot as plt
import cv2

import subprocess
from PIL import Image

os.listdir('../mnt')

!pip install kaggle

!mkdir .kaggle

import json
token = {"username":"nirvana137", "key":"59636e93f7f1e081348b090daf4081a7"}
with open('/content/.kaggle/kaggle.json', 'w') as file:
  json.dump(token, file)

!cp /content/.kaggle/kaggle.json ~/.kaggle/kaggle.json

!kaggle config set -n path -v{/content}

!chmod 600 /root/.kaggle/kaggle.json

!kaggle competitions download -c data-science-bowl-2018 -p /content/kaggle -p /content

!mkdir nuclei_data

!mkdir nuclei_data/stage1_train

os.listdir('nuclei_data')

subprocess.call('unzip  stage1_train.zip -d nuclei_data/stage1_train/ ', shell = True)

subprocess.call('unzip  stage1_test.zip -d nuclei_data/stage1_test/ ', shell = True)

batch_size = 10
img_width = 128
img_height =128
img_channels =3
train_path = 'nuclei_data/stage1_train/'
test_path = 'nuclei_data/stage1_test/'

warnings.filterwarnings('ignore', category=UserWarning, module='skimage')
seed = 42

train_img={}
img_id=[]
img_array=[]
for files in os.listdir(train_path):
    path = train_path + files + '/images/' + files +'.png'
    im = Image.open(path)
    im= np.asarray(im)
    train_img[files+'.png'] = im
    img_id.append(files+'.png')
    img_array.append(im)

img_id

plt.imshow(img_array[6])
len(img_array)

train_mask_dict={}
mask_array=[]
for files in os.listdir('nuclei_data/stage1_train'):
    arr=0
    for file in os.listdir('nuclei_data/stage1_train/'+files+'/masks/'):
        path = 'nuclei_data/stage1_train/'+ files + '/masks/' + file
        im1=Image.open(path)
        im1= np.asarray(im1)
        mask = cv2.resize(im1, (256,256))
        arr = arr + mask
        
    train_mask_dict[files+'.png'] = arr

    mask_array.append(arr)

plt.imshow(mask_array[6])
mask_array[6].shape
len(mask_array)

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(img_array[0])
plt.title('Image')
plt.subplot(1,3,2)
plt.imshow(mask_array[0])
plt.title('Ground truth')
plt.show()

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(img_array[77])
plt.title('Image')
plt.subplot(1,3,2)
plt.imshow(mask_array[77])
plt.title('Ground truth')
plt.show()

def preprocessing(img,mask,SIZE):
    img = img[:,:,:3]
    img = cv2.resize(img, SIZE)
    mask = cv2.resize(mask, SIZE)
   
    img = img/255.
    mask = mask/255.
    mask = np.expand_dims(mask, axis=2)
    return (img,mask)

input_img=[]
output_mask=[]
for i,k in tqdm(zip(img_array,mask_array)):
    processed=preprocessing(i,k,(256,256))
    input_img.append(processed[0])
    output_mask.append(processed[1])

input_img[0].shape

output_mask[0].shape

input_img = np.asarray(input_img)
output_mask = np.asarray(output_mask)

train_img, val_img= input_img[:550], input_img[550:]
train_mask, val_mask = output_mask[:550], output_mask[550:]

test_img={}
test_img_id=[]
test_img_array=[]
for files in os.listdir('nuclei_data/stage1_test'):
    path = 'nuclei_data/stage1_test/'+ files + '/images/' + files +'.png'
    im = Image.open(path)
    im= np.asarray(im)
    test_img[files+'.png'] = im
    test_img_id.append(files+'.png')
    test_img_array.append(im)

test_img_array[7].shape

def preprocessing_test(img,SIZE):
    img = img[:,:,:3]
    img = cv2.resize(img, SIZE)
   
    img = img/255.
    return img

test_img_array[7].shape

test_input=[]
for i in tqdm(test_img_array):
    processed=preprocessing_test(i,(256,256))
    test_input.append(processed)

test_input=np.asarray(test_input)

plt.imshow(test_input[1])

!mkdir model

from keras import models
from keras.models import Model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Activation, UpSampling2D, BatchNormalization
from keras.optimizers import RMSprop

from model.losses import bce_dice_loss, dice_loss, dice_coeff

from keras.losses import binary_crossentropy
import keras.backend as K
from keras.optimizers import Adam

import model.u_net as unet

model = unet.get_unet(num_classes=1)

model.summary()

model.fit(train_img, train_mask, epochs=50, verbose=2, validation_data=(val_img,val_mask), batch_size=1)

model.save_weights('nuclei_segmentation_weights.h5')

model.load_weights('nuclei_segmentation_weights.h5')

plt.imshow(test_input[0])

pred=model.predict(test_input[0].reshape(-1,256,256,3))

pred.shape

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(test_input[0])
plt.title('Test Image')
plt.subplot(1,3,2)
plt.imshow(pred.reshape(256,256))
plt.title('Predicted masks')
plt.show()

pred=model.predict(test_input[1].reshape(-1,256,256,3))

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(test_input[1])
plt.title('Test Image')
plt.subplot(1,3,2)
plt.imshow(pred.reshape(256,256))
plt.title('Predicted masks')
plt.show()

pred = model.predict(test_input[7].reshape(-1, 256, 256, 3))

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(test_input[7])
plt.title('Test Image')
plt.subplot(1,3,2)
plt.imshow(pred.reshape(256,256))
plt.title('Predicted masks')
plt.show()

pred = model.predict(test_input[19].reshape(-1, 256, 256, 3))

plt.figure(figsize = (15, 7))
plt.subplot(1,3,1)
plt.imshow(test_input[19])
plt.title('Test Image')
plt.subplot(1,3,2)
plt.imshow(pred.reshape(256,256))
plt.title('Predicted masks')
plt.show()

