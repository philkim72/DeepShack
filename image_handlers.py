import abc
from collections import OrderedDict

import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.io


class BaseImageLoader(metaclass=abc.ABCMeta):
    def __init__(self, new_shape, gaussian_ksize):
        # Configuration
        self.org_shape = None
        self.new_shape = new_shape
        self.gaussian_ksize = gaussian_ksize

        # Image data
        self.x = None
        self.y = None
        self.annots = None
        self.counts = None

    @abc.abstractmethod
    def load_annotations(self):
        """
        1) Read annotation from MATLAB file for mall dataset and
        from db for ShackCam image
        2) Set self.annots an self.counts
        """
        pass

    @abc.abstractmethod
    def load_data(self):
        """
        This is the main function that users call.

        1) Calls self.load_annotations
        2) Set self.x and self.y
        """
        pass

    def load_image(self, filepath):
        """
        Read an image, reshape to self.new_shape, then divide by 255
        """
        org_img = cv2.imread(filepath)
        new_img = cv2.resize(org_img, self.new_shape)
        self.org_shape = org_img.shape
        return new_img / 255

    def load_gaussian_image(self, annots):
        """
        Create a (x, y, 1) dimension image by applying Gaussian kernel
        Annotations are (x, y) but numpy pixels are (y, x).
        """
        new_shape = self.new_shape[0]//4, self.new_shape[1]//4
        y_scaler = new_shape[0]/self.org_shape[0]
        x_scaler = new_shape[1]/self.org_shape[1]
        img = np.zeros(new_shape)

        for x, y in annots:
            x_scaled = int(round(x * x_scaler))
            y_scaled = int(round(y * y_scaler))

            # Discard annotations that are out of the frame
            if x_scaled < new_shape[0] and y_scaled < new_shape[1]:
                img[y_scaled, x_scaled] += 1

        ksize = (self.gaussian_ksize, self.gaussian_ksize)
        img = cv2.GaussianBlur(src=img, ksize=ksize, sigmaX=0)
        img = np.expand_dims(img, axis=-1)
        return img

    def plot_images(self, index):
        """Plot an image and annotated image side by side"""
        figs, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(self.x[index])
        axes[1].imshow(self.y[index][:, :, 0])  # from 3D to 2D


class MallImageLoader(BaseImageLoader):
    def __init__(self, new_shape=(224, 224), gaussian_ksize=15, image_dir='.'):
        super().__init__(new_shape, gaussian_ksize)
        self.image_dir = image_dir

    def load_annotations(self, filepath):
        """Read a MATLAB file"""
        annots, counts = OrderedDict(), OrderedDict()
        mat = scipy.io.loadmat(filepath)

        for i, sub in enumerate(mat['frame'][0]):
            filename = f"seq_{i+1:06d}.jpg"
            annots[filename] = sub[0][0][0]
            counts[filename] = len(sub[0][0][0])

        self.annots = annots
        self.counts = counts

    def load_data(self):
        """Read annotations, images, and annotated Gaussian images"""
        # Load annotations
        dir_ = self.image_dir
        self.load_annotations(f"{dir_}/mall_dataset/mall_gt.mat")

        # Load image and gaussian image
        x, y = [], []
        for fn, img_annots in self.annots.items():
            img = self.load_image(f"{dir_}/mall_dataset/frames/{fn}")
            gaussian_img = self.load_gaussian_image(self.annots[fn])
            x.append(img)
            y.append(gaussian_img)

        self.x = np.array(x)
        self.y = np.array(y)


class ShackImageLoader(metaclass=abc.ABCMeta):
    def load_annotations(self, filepath):
        # TODO
        pass

    def load_data(self):
        # TODO
        pass
