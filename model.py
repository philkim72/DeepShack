from tensorflow.keras.layers import (Activation, BatchNormalization, Conv2D,
                                     Input, MaxPooling2D, concatenate)
from tensorflow.keras.models import Model
from tensorflow.keras.utils import plot_model


def MSB(filters):
    def func(inputs, bn=False):
        params = {'activation': 'relu', 'padding': 'same'}
        outputs = concatenate([Conv2D(filters, 9, **params)(inputs),
                               Conv2D(filters, 7, **params)(inputs),
                               Conv2D(filters, 5, **params)(inputs),
                               Conv2D(filters, 3, **params)(inputs)])
        if bn:
            outputs = BatchNormalization()(outputs)
            outputs = Activation('relu')(outputs)
        return outputs

    return func


def MSCNN(input_shape):
    inputs = Input(shape=input_shape)

    # Feature Remap
    outputs = Conv2D(filters=64, kernel_size=9, activation='relu', padding='same')(inputs)

    # Multi-scale Feature
    outputs = MSB(4 * 16)(outputs)
    outputs = MaxPooling2D()(outputs)

    # Multi-scale Feature
    outputs = MSB(4 * 32)(outputs)
    outputs = MSB(4 * 32)(outputs)
    outputs = MaxPooling2D()(outputs)

    # Multi-scale Feature
    outputs = MSB(3 * 64)(outputs)
    outputs = MSB(3 * 64)(outputs)

    # Density Map Regression
    outputs = Conv2D(filters=1000, kernel_size=1, activation='relu')(outputs)
    outputs = Conv2D(filters=1, kernel_size=1, activation='relu')(outputs)

    model = Model(inputs=inputs, outputs=outputs)

    plot_model(model, to_file='mscnn.png', show_shapes=True)
    return model
