from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import cv2


def load_annotations(filepath):
    annots = OrderedDict()
    counts = OrderedDict()
    mat = scipy.io.loadmat(filepath)
    for i, sub in enumerate(mat['frame'][0]):
        filename = f"seq_{i+1:06d}.jpg"
        annots[filename] = sub[0][0][0]
        counts[filename] = len(sub[0][0][0])

    return annots, counts


def load_image(filepath, new_shape):
    img = cv2.imread(filepath)
    img = cv2.resize(img, new_shape)
    return img


def load_gaussian_image(img_annots, org_shape, new_shape):
    kernel_size = 15

    y_scaler = new_shape[0]/org_shape[0]
    x_scaler = new_shape[1]/org_shape[1]
    img = np.zeros(new_shape)

    for x, y in img_annots:
        x_scaled = int(x * x_scaler)
        y_scaled = int(y * y_scaler)

        # Discard bad annotation
        if (x_scaled < new_shape[0]) and (y_scaled < new_shape[1]):
            img[y_scaled, x_scaled] = 1

    img = cv2.GaussianBlur(src=img, ksize=(kernel_size, kernel_size), sigmaX=0)
    return img


def plot_images(img1, img2):
    figs, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img1)
    axes[1].imshow(img2)


def load_images():
    org_shape = (480, 640)
    new_shape = (224, 224)

    x = []
    y = []

    annots, counts = load_annotations('mall_dataset/mall_gt.mat')
    for filename, img_annots in annots.items():
        img = load_image(f"mall_dataset/frames/{filename}", new_shape)
        gaussian_img = load_gaussian_image(annots[filename], org_shape, new_shape)
        x.append(img)
        y.append(gaussian_img)

    return x, y
