from PIL import Image, ImageOps
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

def extract(slide, location_width, location_height, extract_size, is_TMA=False):
    if not is_TMA:
        patch = slide.read_region(
            (location_width, location_height), 0, (extract_size, extract_size)).convert('RGB')
    else:
        patch = slide.crop((location_width, location_height, location_width+extract_size, location_height+extract_size))
    return patch

def resize(patch, resize_size):
    return patch.resize((resize_size, resize_size), resample=Image.LANCZOS)

def expand(os_slide, patch_size, annotation_overlap):
    """Function expand the size of TMA cores

    Parameters
    ----------
    os_slide : PIL Image
        A pillow image contains a pillow image
    patch_size : int
        size of extracted patches
    annotation_overlap: float
        the value of acceptable overlap between patch and label

    Returns
    -------
        os_slide : PIL Image
            A expanded image
    """
    # Expand image with border of (1+0.2-annotation_overlap))*patch_size
    border = int((1+0.3-annotation_overlap)*patch_size)
    pixel  = os_slide.load()

    fill   = np.array([0, 0, 0])
    # fill with the average of 9 first pixels
    for i in range(3):
        for j in range(3):
            fill += np.array(pixel[i,j])
    fill = fill // 9
    os_slide = ImageOps.expand(os_slide, border, fill=tuple(fill))
    return os_slide

def extract_and_resize(slide, location_width, location_height, extract_size, resize_size, is_TMA=False):
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

    is_TMA: bool
        it is TMA or not

    Returns
    -------
    patch : Pillow image
        A resized patch
    """
    # if the slide is TMA core, it is PIL image
    if not is_TMA:
        patch = slide.read_region(
            (location_width, location_height), 0, (extract_size, extract_size)).convert('RGB')
    else:
        patch = slide.crop((location_width, location_height, location_width+extract_size, location_height+extract_size))
    if extract_size != resize_size:
        patch = patch.resize((resize_size, resize_size),
                             resample=Image.LANCZOS)
    return patch
