from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import (Activation, BatchNormalization, Conv2D,
                                     Input, MaxPooling2D, concatenate, Dense,
                                     Flatten, Dropout)
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
import pandas as pd


class MultiScaleCNN(object):
    def __init__(self, input_shape, name, fc=False, trainable=True, image_dir='.'):
        self.image_dir = image_dir

        if fc:
            self.model = self._mscnn_fc(input_shape)
            self.name = f'{name}_mscnn_fc'
        else:
            self.model = self._mscnn(input_shape, trainable)
            self.name = f'{name}_mscnn'

        plot_model(self.model, show_shapes=True,
                   to_file=f'{self.image_dir}/results/{self.name}.png')
        self.model.summary()

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

    def _mscnn(self, input_shape, trainable):
        """multi-scale convolutional neural network"""
        inputs = Input(shape=input_shape)

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
        outputs = Conv2D(filters=1, kernel_size=1, activation='relu')(outputs)

        model = Model(inputs=inputs, outputs=outputs)
        model.trainable = trainable

        return model

    def _mscnn_fc(self, input_shape):
        model = Sequential([
            self._mscnn(input_shape, trainable=False),
            MaxPooling2D(),
            Flatten(),
            Dropout(0.5),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(1, activation='relu')
        ])

        return model

    def train(self, x_train, y_train, epochs=30, batch_size=256,
              lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.001):
        # opt = SGD(lr=1e-5, momentum=0.9, decay=0.0005)
        opt = Adam(lr=lr, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, decay=decay)
        self.model.compile(optimizer=opt, loss='mse')

        fn_base = f'{self.image_dir}/results/{self.name}'
        mc = ModelCheckpoint(fn_base + '_weights_{epoch:03d}.h5',
                             save_weights_only=True)
        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size,
                       validation_split=0.1, verbose=1, callbacks=[mc])

        # Save the model and results
        self.model.save_weights(fn_base + '_weights.h5')
        self.model.save(fn_base + '_model.h5')

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

    def load_weights(self, filename):
        self.model.load_weights(filename)
