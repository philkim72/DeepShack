# Model Training

## DESCRIPTION

Our deep learning model has two compenents operating in series:

1. Convolutional neural network VGG16.
2. Fully Connected (FC) Neural Network.

Training Parameters:

* Optimizer: Adam
* Number of epochs: 100
* Batch size: 128
* Learning rate: 0.001

## DEPENDENCIES

* Machine Learning Library: TensorFlow, Keras
* Other Python libraries: pandas, matplotlib, PIL, cv2
* Ipython Jupyter notebooks

## INPUT

Raw data: [annotated Shake Shack images](https://github.com/dimroc/count/tree/master/ml/data/shakecam) courtesy of [Dimroc](https://github.com/dimroc/count/tree/master/ml/data/shakecam)

Since the image set we are using is annotated for people waiting in line only, instead of training directly on raw data, we apply a mask in order to wipe out the areas of the image where people are likely to be standing but are NOT in the queue. By doing this, we can achieve a more accurate prediction.

## OUTPUT

The trained model and weights are saved in h5 format in AWS S3 bucket