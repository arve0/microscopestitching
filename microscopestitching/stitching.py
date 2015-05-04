import imreg_dft as imreg
from skimage.io import imread
#from skimage.feature import register_translation
from itertools import product
import numpy as np
from joblib import Parallel, delayed

from multiprocessing import cpu_count
try:
    _CPUS = cpu_count()
except NotImplementedError:
    # default to 4 on failure
    _CPUS = 4


def stitch(images):
    """Stitch regular spaced images.

    Parameters
    ----------
    images : list of tuple (path, row, column)
        Each image-tuple should contain path, row and column.

        Example:
        >>> images = [('1.png', 0, 0), ('2.png', 0, 1)]

    Returns
    -------
    ndarray
        Merged image.
    """
    ic = ImageCollection(images)

    # calculate translations
    translations = []
    for dim in (0, 1):
        w = Parallel(n_jobs=_CPUS)
        res = w(delayed(get_translation)(dim, i, ic) for i in ic.images)
        res = _remove_none(res)
        translations.append(res)

    # for slice notation
    y_translations = np.array(translations[0])
    x_translations = np.array(translations[1])

    # check that they are regular spaced
    xoffset = np.median(y_translations[:, 1])
    if xoffset != 0:
        print("Warning: Expected rows to have zero x-offset. "
              "Offset found: %s" % xoffset)

    yoffset = np.median(x_translations[:, 0])
    if yoffset != 0:
        print("Warning: Expected columns to have zero y-offset. "
              "Offset found: %s" % yoffset)

    yoffset = np.median(y_translations[:, 0])
    xoffset = np.median(x_translations[:, 1])

    assert yoffset < 0, "Row offset should be negative"
    assert xoffset < 0, "Column offset should be negative"

    if xoffset != yoffset:
        print('Warning: yoffset != xoffset: %4f != %4f' % (yoffset, xoffset))

    # assume all images have the same shape
    img1 = imread(ic.images[0].path)
    y, x = img1.shape
    height = y*ic.number_of_rows + yoffset*(ic.number_of_rows-1)
    width = x*ic.number_of_cols + xoffset*(ic.number_of_cols-1)

    # last dimension is number of images on top of each other
    merged = np.zeros((height, width, 2), dtype=np.int)
    for r, c in product(ic.rows, ic.cols):
        mask = merge_slice(r, c, y, x, yoffset, xoffset)
        # last dim is used for averaging the seam
        img = _add_ones_dim(imread(ic.image(r, c)))
        merged[mask] += img

    # average seam, possible improvement: use gradient
    merged[..., 0] /= merged[..., 1]

    return merged[..., 0].astype(np.uint8)


def get_translation(dim, img, ic):
    """
    Parameters
    ----------
    dim : int
        Which dimension to look for next image. 0 will look for image
        below given row, col, anything else will look to the right for
        ic.image(row, col).
    img : Image
        Image object with properties path, row and col.
    ic : ImageCollection
        Collection which hold neighbor images.

    Returns
    -------
    tuple
        (y_translation, x_translation, row, col)
    """
    row = img.row
    col = img.col

    if dim == 0:
        # img1 on top of img2
        next_row = row+1
        next_col = col
    else:
        # img1 to the left of img2
        next_row = row
        next_col = col+1

    img1_path = ic.image(row, col)
    img2_path = ic.image(next_row, next_col)

    if not img2_path:
        # at the end
        return

    img1 = imread(img1_path)
    img2 = imread(img2_path)

    #tr, _, __ = register_translation(img1, img2, upsample_factor=100)
    tr, _ = imreg.translation(img1, img2)
    return tr[0], tr[1], row, col



def merge_slice(row, col, height, width, yoffset, xoffset):
    ystart = row*(height + yoffset)
    xstart = col*(width + xoffset)
    return slice(ystart, ystart+height), slice(xstart, xstart+width)



class Image:
    def __init__(self, path, row, col):
        self.path = path
        self.row = row
        self.col = col



class ImageCollection:
    def __init__(self, image_list):
        self.image_list = image_list
        self.images = [Image(*i) for i in image_list]


    def image(self, row, col):
        return next((img[0] for img in self.image_list
                     if img[1] == row and img[2] == col), '')


    @property
    def rows(self):
        return sorted(set([i[1] for i in self.image_list]))


    @property
    def cols(self):
        return sorted(set([i[2] for i in self.image_list]))


    @property
    def number_of_rows(self):
        return len(set([i[1] for i in self.image_list]))


    @property
    def number_of_cols(self):
        return len(set([i[2] for i in self.image_list]))


def _add_ones_dim(arr):
    "Adds a dimensions with ones to array."
    arr = arr[..., np.newaxis]
    return np.concatenate((arr, np.ones_like(arr)), axis=-1)


def _remove_none(list_):
    "Remove None objects from list."
    return [o for o in list_ if o != None]
