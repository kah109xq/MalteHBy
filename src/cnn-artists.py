
import argparse

import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

from sklearn.metrics import classification_report

from utils.utils import setting_default_data_dir, setting_default_out_dir



def main(args):

    print("Initiating some awesome convolutional neural networks!")

    # Importing arguments from the arguments parser

    random_state = args.rs

    batch_size = 32
img_height = 180
img_width = 180

    data_dir = args.dd

    test_size = args.ts

    scaling = args.s

    minmax = args.mm

    epochs = args.e

    early_stopping = args.es

    nn_mnist = NeuralNetworkMNIST()

    X_train, X_test, y_train, y_test = nn_mnist.split_and_preprocess_data(random_state=random_state,
                                                                          test_size=test_size,
                                                                          scaling=scaling,
                                                                          minmax=minmax)

    nn_model = nn_mnist.train(X_train, y_train, epochs=epochs, early_stopping=early_stopping)

    nn_mnist.print_eval_metrics(nn_model, X_test, y_test)

    print("DONE! Have a nice day. :-)")


class CNNClassification:

    def __init__(self):

        
            
        

    def preprocess_data(self, train_data_dir, val_data_dir, img_height, img_width, batch_size, random_state=1):
        """Splits the data into a train/test-split

        Args:
            random_state (int, optional): The random state. Defaults to 9.
            train_size (int, optional): Size of the training data. Defaults to 7500.
            test_size (int, optional): Size of the test data. Defaults to 2500.

        Returns:
            X_train, X_test, y_train, y_test: Train/test-split of the data.
        """
        
        self.train_data_dir = train_data_dir

        self.val_data_dir = val_data_dir

        if train_data_dir is None:

            self.train_data_dir, _ = setting_default_data_dir(assignment=5)

        if val_data_dir is None:

            _, self.val_data_dir = setting_default_data_dir(assignment=5)

        self.train_ds = tf.keras.preprocessing.image_dataset_from_directory(self.train_data_dir,
                                                                            seed=random_state,
                                                                            image_size=(img_height, img_width),
                                                                            batch_size=batch_size)

        self.val_ds = tf.keras.preprocessing.image_dataset_from_directory(self.val_data_dir,
                                                                          seed=random_state,
                                                                          image_size=(img_height, img_width),
                                                                          batch_size=batch_size)

        # Preprocessing data for evaluation and classification report

        self.val_images = np.concatenate([images for images, labels in self.val_ds], axis=0)

        val_labels = np.concatenate([labels for images, labels in self.val_ds], axis=0)

        self.train_class_names = self.train_ds.class_names

        self.val_class_names = self.val_ds.class_names

        self.num_classes = len(self.train_class_names)

        # Setting up dataset performance configurations

        AUTOTUNE = tf.data.AUTOTUNE  # Letting tensorflow autotune the buffer size

        self.train_ds = self.train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)  # Caching and shuffling of training data

        self.val_ds = self.val_ds.cache().prefetch(buffer_size=AUTOTUNE)  # Caching validaton data

    def create_model(self, img_height, img_width, print_model=True):

        self.model = Sequential([layers.experimental.preprocessing.Rescaling(1. / 255, input_shape=(img_height, img_width, 3)),
                                 layers.Conv2D(16, 3, padding='same', activation='relu'),
                                 layers.MaxPooling2D(),
                                 layers.Conv2D(32, 3, padding='same', activation='relu'),
                                 layers.MaxPooling2D(),
                                 layers.Conv2D(64, 3, padding='same', activation='relu'),
                                 layers.MaxPooling2D(),
                                 layers.Flatten(),
                                 layers.Dense(128, activation='relu'),
                                 layers.Dense(self.num_classes)
                                 ])

        self.model.compile(optimizer='adam',
                           loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                           metrics=['accuracy'])

        if print_model:

            self.model.summary()

    def train(self, epochs=10):

        history = self.model.fit(self.train_ds,
                                 validation_data=self.val_ds,
                                 epochs=epochs
                                 )

        return history

    def plot_training(self, history):

        acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']

        loss = history.history['loss']
        val_loss = history.history['val_loss']

        epochs_range = range(epochs)

        plt.figure(figsize=(8, 8))
        plt.subplot(1, 2, 1)
        plt.plot(epochs_range, acc, label='Training Accuracy')
        plt.plot(epochs_range, val_acc, label='Validation Accuracy')
        plt.legend(loc='lower right')
        plt.title('Training and Validation Accuracy')

        plt.subplot(1, 2, 2)
        plt.plot(epochs_range, loss, label='Training Loss')
        plt.plot(epochs_range, val_loss, label='Validation Loss')
        plt.legend(loc='upper right')
        plt.title('Training and Validation Loss')
        plt.show()

    def evaluate_model(self):

        predictions = self.model.predict(self.val_images, batch_size=32)

        print(classification_report(self.val_labels,
                                    predictions.argmax(axis=1),
                                    target_names=self.val_class_names))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--rs',
                        metavar="Random State",
                        type=int,
                        help='Random State of the logistic regression model.',
                        required=False,
                        default=1)

    parser.add_argument('--ts',
                        metavar="Test Size",
                        type=int,
                        help='The test size of the test data.',
                        required=False,
                        default=2500)

    parser.add_argument('--s',
                        metavar="Scaling",
                        type=bool,
                        help='Whether to scale the data of not to.',
                        required=False,
                        default=False)

    parser.add_argument('--mm',
                        metavar="MinMax",
                        type=bool,
                        help='Whether to MinMax normalize the data of not to.',
                        required=False,
                        default=True)

    parser.add_argument('--e',
                        metavar="Epochs",
                        type=int,
                        help='Number of epochs for the neural network training.',
                        required=False,
                        default=100)

    parser.add_argument('--es',
                        metavar="Early Stopping",
                        type=bool,
                        help='Whether to stop the training before overfitting the data.',
                        required=False,
                        default=True)

    main(parser.parse_args())