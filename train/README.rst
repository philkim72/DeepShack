=========================
Model Training
=========================

Our deep learning model has two compenents operating in series:

1. Multi-Scale Convolutional Neural Network (MSCNN)
2. Fully Connected (FC) Neural Network.

This architecture was inspired by Zeng et al. and the paper `Multi-Scale Convolutional Neural Networks for Crowd Counting <https://arxiv.org/pdf/1702.02359.pdf>`_ .

1. The first component (MSCNN) takes an image as input and produces a Gaussian blur density map as output.
2. The second fully connected neural network takes a the density map as input and produces a count of people in the image as output.

To train the MSCNN (1), we use a publicly available and annotated `shopping mall dataset <personal.ie.cuhk.edu.hk/~ccloy/downloads_mall_dataset.html>`_ to train the network and used annotated Shack camera data to perform additional training throughtransfer learning.

To train the FC layer (2), we used the annotated Shack camera data (i.e. images labelled with counts of people in line). Rather than sending the output of MSCNN directly to FC network, we apply a mask in order to wipe out the areas of the image where people are likely to be standing but are NOT in the queue. By doing this, we can achieve a more accurate prediction.


Prerequisites
=============

Model training has several dependencies:

1. Machine Learning Library: Tensor Flow
2. Other Python libraries: pandas, matplotlib, PIL, cv2
3. Training data: `shopping mall dataset <personal.ie.cuhk.edu.hk/~ccloy/downloads_mall_dataset.html>`_ and `annotated Shake Shack images <https://github.com/dimroc/count/tree/master/ml/data/shakecam>`_ courtesy of `Dimroc <https://github.com/dimroc/count/tree/master/ml/data/shakecam>`_.
4. ipython Jupyter notebooks


Deployment
=============

Two deep learning models were successfully trained locally in a Jupyter notebook. Although our initial plan was to deploy the models to AWS Lambda, our model exceed the AWS Lambda storage limits.

We are actively exploring two alternatives to AWS Labmda that will meet our storage needs and integrate easily with the rest of our application. Specifically:

1. AWS Elastic Container Service
2. AWS SageMaker

Each component can be readily integrated with AWS Lambda via API calls (provided by AWS API Gateway).

To run Jupyter notebook with Docker
============================
You could run Jupyter Notebook with Docker, which comes with Python3.5 and TensorFlow. Update ``requirements.txt`` if you want to add Python packages.


   docker build --tag=deepshack .
   docker run -it --rm -v $(pwd):/tf/DeepShack -p 9999:9999 deepshack
   http://localhost:9999
