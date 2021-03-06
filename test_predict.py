import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import seaborn as sns
import os
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from sklearn.preprocessing import LabelEncoder
from keras.utils.np_utils import to_categorical
from keras.models import Sequential # to create a cnn model
from keras.models import load_model, Model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D, Input
from keras.applications.vgg16 import VGG16
from keras.optimizers import RMSprop,Adam
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau
import pickle


def prepareImages(train, shape, path):
    
    x_train = np.zeros((shape, 224, 224, 3))
    count = 0
    
    for fig in train['Image']:
        
        #load images into images of size 100x100x3
        img = image.load_img(os.path.join(path, fig), target_size=(224, 224, 3))
        # print(img.shape)
        x = image.img_to_array(img)
        x = preprocess_input(x)
        x_train[count] = x
        if (count%500 == 0):
            print("Processing image: ", count+1, ", ", fig)
        count += 1
    
    return x_train

if __name__=="__main__":

    train = pd.read_csv('subset_train.csv')
    y_train = train["Id"]
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)

    newwhale = pd.read_csv("sample_submission.csv")
    x_newwhale = prepareImages(newwhale, newwhale.shape[0], "crop_test")
    x_newwhale /= 255.0
    model = load_model('data/model_crop_aug.h5')
    predictions = model.predict(np.array(x_newwhale))
    np.save("data/test_scores.npy", predictions)
    for i, pred in enumerate(predictions):
        scores = pred[pred.argsort()[-5:]]
        newwhale_location = np.where(scores<0.1)[0]
        candidates = label_encoder.inverse_transform(pred.argsort()[-5:][::-1])
        if len(newwhale_location)>0:
            candidates = np.insert(candidates, 4-np.amax(newwhale_location), 'new_whale')
            candidates = candidates[:-1]        
        newwhale.loc[i, 'Id'] = ' '.join(candidates)
    newwhale.to_csv("data/test_prediction_2.csv", index=False)
