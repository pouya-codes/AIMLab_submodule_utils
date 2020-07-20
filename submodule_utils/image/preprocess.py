from PIL import Image
import numpy as np

def check_luminance(np_image, blank_thresh=210, blank_percent=0.75):
    """Function to check the patch is background or not

    Parameters
    ----------
    np_image : numpy array
        A pillow image contains a pillow image

    is_eval : bool
        If true, it returns a 4D tensor
        If false, it returns a 3D tensor

    Returns
    -------
        Return true if it is not background
    """
    image_luminance = 0.2126 * np_image[:, :, 0] + \
        0.7152 * np_image[:, :, 1] + 0.0722 * np_image[:, :, 2]
    return np.mean(image_luminance > blank_thresh) < blank_percent

def pillow_image_to_ndarray(image):
    return np.asarray(image).copy()

def extract(slide, location_width, location_height, extract_size):
    return slide.read_region(
        (location_width, location_height), 0, (extract_size, extract_size)
    ).convert('RGB')

def resize(patch, resize_size):
    return patch.resize((resize_size, resize_size), resample=Image.LANCZOS)

def extract_and_resize(slide, location_width, location_height, extract_size, resize_size):
    """Function to extract a patch from slide at (location_width, location_height) and then resize
        using Lanczos resampling filter

    Parameters
    ----------
    slide : OpenSlide object
        An numpy array contains a pillow image

    location_width : int
        Patch location width

    location_height : int
        Patch location height

    extract_size : int
        Extract patch size

    resize_size : int
        Resize patch size

    Returns
    -------
    patch : Pillow image
        A resized patch
    """
    patch = slide.read_region(
        (location_width, location_height), 0, (extract_size, extract_size)).convert('RGB')
    if extract_size != resize_size:
        patch = patch.resize((resize_size, resize_size),
                             resample=Image.LANCZOS)
    return patch
