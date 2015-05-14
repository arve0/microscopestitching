import imreg_dft as imreg
from skimage.io import imread
#from skimage.feature import register_translation
from itertools import product
import numpy as np
from joblib import Parallel, delayed
from warnings import warn

from multiprocessing import cpu_count
try:
    _CPUS = cpu_count()
except NotImplementedError:
    # default to 4 on failure
    _CPUS = 4


def calc_translations_parallel(images):
    """Calculate image translations in parallel.

    Parameters
    ----------
    images : ImageCollection
        Images as instance of ImageCollection.

    Returns
    -------
    2d array, (ty, tx)
        ty and tx is translation to previous image in respectively
        x or y direction.
    """
    w = Parallel(n_jobs=_CPUS)
    res = w(delayed(images.translation)(img) for img in images)
    return np.array(res)


def stitch(images):
    """Stitch regular spaced images.

    Parameters
    ----------
    images : ImageCollection or list of tuple(path, row, column)
        Each image-tuple should contain path, row and column. Row 0,
        column 0 is top left image.

        Example:
        >>> images = [('1.png', 0, 0), ('2.png', 0, 1)]

    Returns
    -------
    ndarray
        Merged image.
    """
    if type(images) != ImageCollection:
        images = ImageCollection(images)
    translations = calc_translations_parallel(images)
    y_translations = translations[:,0]
    x_translations = translations[:,1]

    # check that they are regular spaced
    xoffset = np.median(y_translations[:, 1])
    if xoffset != 0:
        warn("Expected rows to have zero x-offset. "
              "Offset found: %s" % xoffset)

    yoffset = np.median(x_translations[:, 0])
    if yoffset != 0:
        warn("Expected columns to have zero y-offset. "
              "Offset found: %s" % yoffset)

    yoffset = np.median(y_translations[:, 0])
    xoffset = np.median(x_translations[:, 1])

    assert yoffset < 0, "Row offset should be negative"
    assert xoffset < 0, "Column offset should be negative"

    if xoffset != yoffset:
        warn('yoffset != xoffset: %s != %s' % (yoffset, xoffset))

    # assume all images have the same shape
    img1 = imread(images[0].path)
    y, x = img1.shape
    height = y*len(images.rows) + yoffset*(len(images.rows)-1)
    width = x*len(images.cols) + xoffset*(len(images.cols)-1)

    # last dimension is number of images on top of each other
    merged = np.zeros((height, width, 2), dtype=np.int)
    for image in images:
        r, c = image.row, image.col
        mask = _merge_slice(r, c, y, x, yoffset, xoffset)
        # last dim is used for averaging the seam
        img = _add_ones_dim(imread(images(r, c).path))
        merged[mask] += img

    # average seam, possible improvement: use gradient
    merged[..., 0] /= merged[..., 1]

    return merged[..., 0].astype(np.uint8)



class Image:
    def __init__(self, path, row=None, col=None):
        self.path = path
        self.row = row
        self.col = col
        self.translation = None


    def __repr__(self):
        return 'Image("%s", row=%s, col=%s)' % (self.path, self.row, self.col)


    def __bool__(self):
        return self.path != ''
    __nonzero__ = __bool__



class ImageCollection:
    def __init__(self, image_list):
        self.image_list = image_list
        self.images = [Image(*i) for i in image_list]


    def image(self, row, col):
        return next((img for img in self.images
                     if img.row == row and img.col == col), Image(''))
    __call__ = image

    def translation(self, img):
        if type(img.translation) == np.ndarray:
            return img.translation
        else:
            # img on top
            top_img = self.image(img.row-1, img.col)
            # img to the left
            left_img = self.image(img.row, img.col-1)

            if top_img:
                img1 = imread(top_img.path)
                img2 = imread(img.path)
                y_translation, _ = imreg.translation(img1, img2)
            else:
                y_translation = (0, 0)

            if left_img:
                img1 = imread(left_img.path)
                img2 = imread(img.path)
                x_translation, _ = imreg.translation(img1, img2)
            else:
                x_translation = (0, 0)

            img.translation = np.array((y_translation, x_translation))
            return img.translation


    @property
    def rows(self):
        return sorted(set([i[1] for i in self.image_list]))


    @property
    def cols(self):
        return sorted(set([i[2] for i in self.image_list]))


    def __iter__(self):
        for img in self.images:
            yield img


    def __getitem__(self, index):
        return self.images[index]


    def __repr__(self):
        return 'ImageCollection(\n  ' + ',\n  '.join([str(i) for i in self]) + ')'



def _add_ones_dim(arr):
    "Adds a dimensions with ones to array."
    arr = arr[..., np.newaxis]
    return np.concatenate((arr, np.ones_like(arr)), axis=-1)


def _merge_slice(row, col, height, width, yoffset, xoffset):
    ystart = row*(height + yoffset)
    xstart = col*(width + xoffset)
    return slice(ystart, ystart+height), slice(xstart, xstart+width)


def _smooth_overlap(img):
    "Create smooth overlap between images."
    # img = np.ones((100,100))
    #
    # img[:10,:]  *= np.linspace(0, 1, 10)[:,np.newaxis]
    # img[:,:10]  *= np.linspace(0, 1, 10)[np.newaxis,:]
    #
    # img[-10:,:] *= np.linspace(1, 0, 10)[:,np.newaxis]
    # img[:,-10:] *= np.linspace(1, 0, 10)[np.newaxis,:]
    #
    # imshow(img)
    pass
