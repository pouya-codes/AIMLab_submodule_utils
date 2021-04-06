import math
import numpy as np
import operator
from PIL import Image, ImageChops

"""Functions are taken from:
http://effbot.org/zone/pil-comparing-images.htm
"""

def equal(im1, im2):
    """Check that two images are equal.
    """
    return ImageChops.difference(im1, im2).getbbox() is None

def rmsdiff(im1, im2):
    """Calculate the root-mean-square difference between two images.

    Update to original effbot function 
    https://stackoverflow.com/questions/3098406/root-mean-square-difference-between-two-images-using-python-and-pil
    """
    errors = np.asarray(ImageChops.difference(im1, im2)) / 255
    return math.sqrt(np.mean(np.square(errors)))

