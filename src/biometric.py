import cv2
import numpy as np
from skimage.morphology import skeletonize


def extract_minutiae(image_path):
    """Load a fingerprint image, binarize and skeletize it, then return a list
    of minutiae coordinates (ridge endings and bifurcations).

    The returned list contains (row, col) tuples in image coordinates.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"cannot read image '{image_path}'")

    # simple preprocessing: blur + Otsu threshold
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # skeletonize expects a boolean image where foreground==True
    skeleton = skeletonize(binary // 255).astype(np.uint8)

    minutiae = []
    h, w = skeleton.shape
    # pad image to simplify neighbour counting
    padded = np.pad(skeleton, 1, mode="constant", constant_values=0)
    for y in range(1, h + 1):
        for x in range(1, w + 1):
            if padded[y, x] == 0:
                continue
            # count 8-connected neighbours (exclude centre pixel)
            neighbourhood = padded[y - 1 : y + 2, x - 1 : x + 2]
            count = int(neighbourhood.sum()) - 1
            # ridge ending (1) or bifurcation (3 or more)
            if count in (1, 3):
                minutiae.append((y - 1, x - 1))
    return minutiae


def generate_template(image_path, grid_size=(16, 16)):
    """Produce a fixed-length binary template from the minutiae set.

    The fingerprint image is divided into ``grid_size`` cells; any cell that
    contains at least one minutia is marked '1'.  The resulting bit pattern is
    returned as a bytes object (packed, big‑endian).
    """
    minutiae = extract_minutiae(image_path)
    if not minutiae:
        # empty template if no minutiae found
        bitgrid = np.zeros(grid_size, dtype=np.uint8)
    else:
        # map coordinates to cell indices
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        bitgrid = np.zeros(grid_size, dtype=np.uint8)
        cell_h = h / grid_size[0]
        cell_w = w / grid_size[1]
        for (y, x) in minutiae:
            i = int(y // cell_h)
            j = int(x // cell_w)
            if i >= grid_size[0]:
                i = grid_size[0] - 1
            if j >= grid_size[1]:
                j = grid_size[1] - 1
            bitgrid[i, j] = 1
    # flatten and pack bits into bytes
    flat = bitgrid.flatten()
    packed = np.packbits(flat, bitorder="big")
    return packed.tobytes()
