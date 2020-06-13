# Dataloader ： utils/loder.pyに記述するべき内容
import numpy as np
import cv2
from math import ceil
from scipy import ndimage
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras import utils
import keras
#from tensorflow.keras.datasets.cifar10 import load_data
from tensorflow.keras.datasets.mnist import load_data
from keras.preprocessing.image import ImageDataGenerator

class Dataloader(object):
    """
    Attributes
    ------------
    x_train, x_valid, x_test : 訓練用，評価用，テスト用入力画像
    y_train, y_valid, y_test : 訓練用，評価用，テスト用出力ラベル

    """

    def __init__(self):
        pass
    
    def get_user_data(self, train_dir, batch_size, validation_dir = None, resize_shape = (255, 255), test_dir = None, test_batch_size=1):
        '''
        ディレクトリ名を指定して画像データのジェネレータを生成する

        Paramteres
        --------------
        train_dir : str
            訓練データのディレクトリへのパス
        batch_size : int
            訓練データ（と検証データ）のバッチサイズ
        validation_dir : str
            検証データのディレクトリへのパス
        resize_shape : tuple
            画像データをこのサイズにリサイズする
        test_dir : str
            テストデータのディレクトリへのパス
        test_batch_size : int
            テストデータのバッチサイズ（デフォルトは1）
        '''
        # 訓練データ
        train_datagen = ImageDataGenerator(
                            rescale=1.0/255,
                            shear_range=0.2,  # これ以降は多分水増し関係の設定
                            zoom_range=0.2,
                            horizontal_flip=True  # 画像を取得するときにランダムに反転する
                        )

        self.train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=resize_shape,
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=True
        )
        
        # 検証データ
        if validation_dir != None:
            validation_datagen = ImageDataGenerator(rescale=1.0/255)

            self.validation_generator = validation_datagen.flow_from_directory(
                validation_dir,
                target_size=resize_shape,
                batch_size=batch_size,
                class_mode='categorical',
                shuffle=True
            )       
        
        # テストデータ
        if test_dir != None:
            test_datagen = ImageDataGenerator(rescale=1.0/255)

            self.test_generator = test_datagen.flow_from_directory(
                test_dir,
                target_size=resize_shape,
                batch_size=1,
                class_mode='categorical',
                shuffle=True
            )
    
    def get_mnist_data(self, resize_mode = False, resize_shape = None, cvtColor_mode = False):
        # load MNIST data
        (x_train, y_train), (x_test, y_test) = load_data()
        x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.175)
        self.x_train = x_train.reshape(x_train.shape[0], 28, 28, 1).astype('float32')/255
        self.x_valid = x_valid.reshape(x_valid.shape[0], 28, 28, 1).astype('float32')/255
        self.x_test = x_test.reshape(x_test.shape[0], 28, 28, 1).astype('float32')/255

        # resize
        if resize_mode == True:
            self.x_train = self.resize(self.x_train, shape = resize_shape)
            self.x_valid = self.resize(self.x_valid, shape = resize_shape)
            self.x_test = self.resize(self.x_test, shape = resize_shape)
            
        # channel がRGBの時（リサイズはどう実装するかは分からない．まとめて出来る？）
        if cvtColor_mode == True:
            self.x_train = self.gray2color(self.x_train)
            self.x_valid = self.gray2color(self.x_valid)
            self.x_test = self.gray2color(self.x_test)
            
        # convert one-hot vector
        self.y_train = keras.utils.to_categorical(y_train, 10)
        self.y_valid = keras.utils.to_categorical(y_valid, 10)
        self.y_test = keras.utils.to_categorical(y_test, 10)
    
        # データ数を絞る
        self.x_train = self.x_train[0:500]
        self.x_valid = self.x_valid[0:500]
        self.x_test = self.x_test[0:500]
        self.y_train = self.y_train[0:500]
        self.y_valid = self.y_valid[0:500]
        self.y_test = self.y_test[0:500]

    def resize(self, img, shape):
        img_resized = []
        for num in range(0, img.shape[0]):
              img_resized.append(list(cv2.resize(img[num], shape)))
        img_resized = np.array(img_resized)
        return img_resized

    def gray2color(self, img):
        img_color = []
        for num in range(0, img.shape[0]):
              img_color.append(list(cv2.cvtColor(img[num], cv2.COLOR_GRAY2RGB)))
        img_color = np.array(img_color)
        return img_color