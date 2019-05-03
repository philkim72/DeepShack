import abc

import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.layers import (Activation, BatchNormalization, Conv2D,
                                     Dense, Dropout, Flatten, Input,
                                     MaxPooling2D, concatenate)
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import plot_model


class BaseModel(metaclass=abc.ABCMeta):
    def __init__(self, input_shape, name, image_dir='.',
                 existing_model_path=None):
        self.input_shape = input_shape
        self.name = name
        self.image_dir = image_dir

        if existing_model_path:
            self.model = load_model(existing_model_path)
        else:
            self.model = self.create_model()

        plot_model(self.model, show_shapes=True,
                   to_file=f'{image_dir}/results/{name}.png')
        self.model.summary()

    @abc.abstractmethod
    def create_model(self):
        pass

    def train(self, x_train, y_train, epochs=30, batch_size=256,
              lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.001):

        fn_base = f'{self.image_dir}/results/{self.name}'

        opt = Adam(lr=lr, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, decay=decay)
        self.model.compile(optimizer=opt, loss='mse')

        mc = ModelCheckpoint(fn_base + '.h5', save_best_only=True, mode='min')
        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size,
                       validation_split=0.1, verbose=1, callbacks=[mc])
        self.model.save(fn_base + '_final.h5')

        df = pd.DataFrame.from_dict(self.model.history.history)
        df.to_csv(fn_base + '_history.csv', index=False)

        # Plot results
        fig, ax = plt.subplots(figsize=(8, 6))
        df.plot(y='loss', kind='line', ax=ax)
        df.plot(y='val_loss', kind='line', ax=ax)

    def evaluate(self, x_test, y_test):
        test_score = self.model.evaluate(x_test, y_test)
        print('Train score:', self.model.history.history['loss'][-1])
        print('Test score:', test_score)


class MultiScaleCNN(BaseModel):
    def _msb(self, filters):
        """Multi-Scale Blob"""
        def func(inputs, bn=False):
            params = {'activation': 'relu', 'padding': 'same',
                      'kernel_regularizer': l2(5e-4)}
            outputs = concatenate([Conv2D(filters, 9, **params)(inputs),
                                   Conv2D(filters, 7, **params)(inputs),
                                   Conv2D(filters, 5, **params)(inputs),
                                   Conv2D(filters, 3, **params)(inputs)])
            if bn:
                outputs = BatchNormalization()(outputs)
                outputs = Activation('relu')(outputs)
            return outputs

        return func

    def create_model(self):
        """multi-scale convolutional neural network"""
        inputs = Input(shape=self.input_shape)

        # Feature Remap
        outputs = Conv2D(filters=64, kernel_size=9,
                         activation='relu', padding='same')(inputs)

        # Multi-scale Feature
        outputs = self._msb(4 * 16)(outputs)
        outputs = MaxPooling2D()(outputs)

        # Multi-scale Feature
        outputs = self._msb(4 * 32)(outputs)
        outputs = self._msb(4 * 32)(outputs)
        outputs = MaxPooling2D()(outputs)

        # Multi-scale Feature
        outputs = self._msb(3 * 64)(outputs)
        outputs = self._msb(3 * 64)(outputs)

        # Density Map Regression
        outputs = Conv2D(filters=1000, kernel_size=1, activation='relu',
                         kernel_regularizer=l2(5e-4))(outputs)
        outputs = Conv2D(filters=1, kernel_size=1, activation='linear')(outputs)

        model = Model(inputs=inputs, outputs=outputs)
        return model


class FullyConnected(BaseModel):
    def create_model(self):
        model = Sequential([
            MaxPooling2D(input_shape=self.input_shape),
            Flatten(),
            Dropout(0.5),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(1, activation='relu')
        ])
        return model
