import cv2
import numpy as np
from skimage.filters import threshold_niblack, threshold_sauvola

def global_threshold(image, thresh=127):
    """Applies global thresholding."""
    _, result = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)
    return result

def mean_adaptive_threshold(image, block_size=11, c=2):
    """Applies mean adaptive thresholding."""
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                 cv2.THRESH_BINARY, block_size, c)

def gaussian_adaptive_threshold(image, block_size=11, c=2):
    """Applies Gaussian adaptive thresholding."""
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, block_size, c)

def otsu_threshold(image):
    """Applies Otsu's binarization method."""
    _, result = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result

def niblack_threshold(image, window_size=25, k=0.8):
    """Applies Niblack's binarization method."""
    thresh_niblack = threshold_niblack(image, window_size=window_size, k=k)
    binary_niblack = image > thresh_niblack
    return (binary_niblack * 255).astype(np.uint8)

def sauvola_threshold(image, window_size=25, k=0.2, r=None):
    """Applies Sauvola's binarization method."""
    thresh_sauvola = threshold_sauvola(image, window_size=window_size, k=k, r=r)
    binary_sauvola = image > thresh_sauvola
    return (binary_sauvola * 255).astype(np.uint8)
