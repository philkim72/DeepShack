import json
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import cv2


class ImageLoader(object):
    def __init__(self, image_dir=None, new_shape=224, gaussian_ksize=15):
        self.org_shape = None
        self.new_shape = (new_shape, new_shape)
        self.gaussian_ksize = (gaussian_ksize, gaussian_ksize)
        self.image_dir = image_dir
        self.c = 4
        self.data = OrderedDict()

    def _read_annotations(self, filepath):
        """Read annotation from a JSON"""
        with open(filepath, 'r') as f:
            annots = json.load(f)

        return annots

    def _read_image(self, filepath):
        """
        Read an image, reshape to self.new_shape, then divide by 255
        """
        org_img = cv2.imread(filepath)
        new_img = cv2.resize(org_img, self.new_shape)
        self.org_shape = org_img.shape
        return new_img / 255

    def _read_gaussian_image(self, annots):
        """
        Create a (x, y, 1) dimension image by applying Gaussian kernel
        Annotations are (x, y) but numpy pixels are (y, x).
        """
        new_shape = self.new_shape[0]//self.c, self.new_shape[1]//self.c
        img = np.zeros(new_shape)
        y_scaler = new_shape[0]/self.org_shape[0]
        x_scaler = new_shape[1]/self.org_shape[1]

        scaled_annots = []
        for x, y in annots:
            x_scaled = int(round(x * x_scaler))
            y_scaled = int(round(y * y_scaler))

            # Discard annotations that are out of the frame
            if x_scaled < new_shape[0] and y_scaled < new_shape[1]:
                img[y_scaled, x_scaled] += 1
                scaled_annots.append((x_scaled, y_scaled))

        gimg = cv2.GaussianBlur(src=img, ksize=self.gaussian_ksize, sigmaX=0)
        gimg = np.expand_dims(gimg, axis=-1)
        return gimg, scaled_annots

    def load_train_data(self):
        """Read annotations, images, and annotated Gaussian images"""
        # Load annotations
        dir_ = self.image_dir
        self.annots = self._read_annotations(f"{dir_}/annotation.json")

        # Load image and gaussian image
        for fn, org_annots in self.annots.items():
            org_img = self._read_image(f"{dir_}/frames/{fn}")
            gaussian_img, scaled_annots = self._read_gaussian_image(org_annots)
            self.data[fn] = {'org_img': org_img,
                             'gaussian_img': gaussian_img,
                             'org_annots': org_annots,
                             'scaled_annots': scaled_annots}

    def plot_image(self, i=None, filename=None):
        """
        Plot an image and annotated image side by side.
        Either pass i or filename
        """
        if isinstance(i, int):
            _, item = list(self.data.items())[i]
        elif filename:
            item = self.data[filename]
        else:
            raise ValueError('Pass either index or filename')

        org_img = item['org_img']
        gaussian_img = item['gaussian_img']
        scaled_annots = item['scaled_annots']

        figs, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Original image
        axes[0].imshow(org_img)

        # Annotation
        img_array = (org_img*255).astype('uint8')
        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)
        for scaled_x, scaled_y in scaled_annots:
            draw.text((scaled_x*self.c, scaled_y*self.c), "X", fill="red")
        axes[1].imshow(img)

        # Gaussian image, converting from 3D to 2D
        axes[2].imshow(gaussian_img[:, :, 0])

    @property
    def org_img(self):
        vec = [v['org_img'] for v in self.annots.values()]
        return np.array(vec).astype(np.float32)

    @property
    def gaussian_img(self):
        vec = [v['gaussian_img'] for v in self.annots.values()]
        return np.array(vec).astype(np.float32)

    @property
    def files(self):
        return self.data.keys()

    @property
    def count(self):
        vec = [len(v) for v in self.annots.values()]
        return np.array(vec).astype(np.float32)


class ShackCamLoader(ImageLoader):
    def __init__(self, image_dir=None, new_shape=224, gaussian_ksize=15):
        ImageLoader.__init__(self, image_dir, new_shape, gaussian_ksize)

        gaussian_shape = (self.new_shape[0]//self.c, self.new_shape[1]//self.c)
        mask = cv2.imread(f"{self.image_dir}/line_mask.png", 0) // 255
        mask = cv2.resize(mask, gaussian_shape)
        self.mask = (mask == 0)

    def mask_img(self, img):
        img = img.copy()
        img[self.mask] = 0
        return img

    @property
    def masked_gaussian_img(self):
        imgs = [self.mask_img(v['gaussian_img']) for v in self.data.values()]
        return np.array(imgs)

    def plot_image(self, i=None, filename=None):
        """
        Plot an image and annotated image side by side.
        Either pass i or filename
        """
        if isinstance(i, int):
            _, item = list(self.data.items())[i]
        elif filename:
            item = self.data[filename]
        else:
            raise ValueError('Pass either index or filename')

        org_img = item['org_img']
        gaussian_img = item['gaussian_img']
        scaled_annots = item['scaled_annots']

        figs, axes = plt.subplots(1, 4, figsize=(20, 5))

        # Original image
        axes[0].imshow(org_img)

        # Annotation
        img_array = (org_img*255).astype('uint8')
        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)
        for scaled_x, scaled_y in scaled_annots:
            draw.text((scaled_x*self.c, scaled_y*self.c), "X", fill="red")
        axes[1].imshow(img)

        # Gaussian image, converting from 3D to 2D
        axes[2].imshow(gaussian_img[:, :, 0])

        axes[3].imshow(self.mask_img(gaussian_img[:, :, 0]))
