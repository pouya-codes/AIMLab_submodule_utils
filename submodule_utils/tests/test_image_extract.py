import os
import pytest
import openslide
from PIL import Image, ImageChops
from openslide import OpenSlide

from submodule_utils.tests import (
        ERR_THRESHOLD,
        OUTPUT_DIR, MOCK_SLIDES_DIR,
        MOCK_PATCHES_512_40_DIR,
        MOCK_PATCHES_256_20_DIR,
        MOCK_PATCHES_128_10_DIR)
import submodule_utils as utils
# import submodule_utils.image as image
from submodule_utils.image.extract import (
        SlideCoordsExtractor, SlidePatchExtractor)

def almost_zero(x):
    return x < ERR_THRESHOLD

class MockOpenSlide(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    @property
    def dimensions(self):
        return (self.width, self.height,)

@pytest.fixture(scope="module")
def mock_slides():
    slides = { }
    for file in os.listdir(MOCK_SLIDES_DIR):
        slide_name = utils.path_to_filename(file)
        os_slide = OpenSlide(os.path.join(MOCK_SLIDES_DIR, file))
        slides[slide_name] = os_slide
    return slides

def test_mock_slides(mock_slides):
    os_image = mock_slides['TCGA-HNSC-1']
    assert type(os_image) == OpenSlide
    assert os_image.level_count == 1
    assert os_image.dimensions == (2040, 1536,)
    # print(os_image.properties)
    # print('level_dimensions', os_image.level_dimensions)
    # print('level_downsamples', os_image.level_downsamples)
    os_image = mock_slides['TCGA-HNSC-2']
    assert type(os_image) == OpenSlide
    assert os_image.level_count == 1
    assert os_image.dimensions == (2040, 1536,)

def test_SlideCoordsExtractor():
    tile_x = 3
    tile_y = 4
    patch_size = 1024
    width = patch_size * tile_x
    height = patch_size * tile_y
    os_slide = MockOpenSlide(width, height)
    sce = SlideCoordsExtractor(os_slide, patch_size)
    assert len(sce) == tile_x * tile_y
    expected_coords = [
            (0, 0, 0 * patch_size, 0 * patch_size),
            (1, 0, 1 * patch_size, 0 * patch_size),
            (2, 0, 2 * patch_size, 0 * patch_size),
            (0, 1, 0 * patch_size, 1 * patch_size),
            (1, 1, 1 * patch_size, 1 * patch_size),
            (2, 1, 2 * patch_size, 1 * patch_size),
            (0, 2, 0 * patch_size, 2 * patch_size),
            (1, 2, 1 * patch_size, 2 * patch_size),
            (2, 2, 2 * patch_size, 2 * patch_size),
            (0, 3, 0 * patch_size, 3 * patch_size),
            (1, 3, 1 * patch_size, 3 * patch_size),
            (2, 3, 2 * patch_size, 3 * patch_size)]
    sce_sorted_result = list(sce)
    assert sce_sorted_result == expected_coords
    sce = SlideCoordsExtractor(os_slide, patch_size, shuffle=True)
    assert len(sce) == tile_x * tile_y 
    sce_shuffled_result = list(sce)
    assert sce_shuffled_result != sce_sorted_result
    assert sorted(sce_shuffled_result, key=lambda x: (x[1]*10000) + x[0]) \
            == expected_coords

@pytest.mark.parametrize("patch_size", [256, 512, 1024])
@pytest.mark.parametrize("tile_y", range(3, 8))
@pytest.mark.parametrize("tile_x", range(3, 8))
@pytest.mark.parametrize("shuffle", [True, False])
def test_SlideCoordsExtractor_param(shuffle, tile_x, tile_y, patch_size):
    width = patch_size * tile_x
    height = patch_size * tile_y
    os_slide = MockOpenSlide(width, height)
    sce = SlideCoordsExtractor(os_slide, patch_size, shuffle=shuffle)
    assert len(sce) == tile_x * tile_y
    expected = []
    for j in range(tile_y):
        for i in range(tile_x):
            expected.append((i, j, i * patch_size, j * patch_size,))
    expected.sort(key=lambda x: (x[1]*10000) + x[0])
    actual = list(sce)
    assert len(actual) == tile_x * tile_y
    if shuffle is True:
        assert actual != expected
    assert sorted(actual, key=lambda x: (x[1]*10000) + x[0]) == expected

def test_SlidePatchExtractor(mock_slides, output_dir):
    os_slide = mock_slides['TCGA-HNSC-2']
    patch_size = 512
    sce = SlideCoordsExtractor(os_slide, patch_size)
    sce_sorted_result = list(sce)
    spe_result = [ ]
    for patch, tile_loc, resized_patches in SlidePatchExtractor(
            os_slide, patch_size):
        tile_x, tile_y, x, y = tile_loc
        spe_result.append(tile_loc)
        assert patch.size == (patch_size, patch_size,)
        assert almost_zero(utils.image.rmsdiff(patch, resized_patches[patch_size]))
        patch.save(os.path.join(output_dir, f"{x}_{y}.png"))
    assert spe_result == sce_sorted_result 
    for file in os.listdir(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2']):
        expected_patchpath = os.path.join(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2'], file)
        expected_patch = Image.open(expected_patchpath)
        actual_patchpath = os.path.join(output_dir, file)
        actual_patch = Image.open(actual_patchpath)
        assert almost_zero(utils.image.rmsdiff(expected_patch, actual_patch))

@pytest.mark.skip
def test_SlidePatchExtractor_to_generate(mock_slides, output_dir):
    patch_size = 512
    resize_sizes = [512, 256, 128]
    resize_sizes_to_path_chunk = {
            512: '512/40',
            256: '256/20',
            128: '128/10'}
    for slide_name, os_slide in  mock_slides.items():
        for patch, tile_loc, resized_patches in SlidePatchExtractor(
                os_slide, patch_size, resize_sizes=resize_sizes):
            tile_x, tile_y, x, y = tile_loc
            for resize_size in resize_sizes:
                os.makedirs(os.path.join(
                        output_dir, slide_name, resize_sizes_to_path_chunk[resize_size]),
                            exist_ok=True)
                resized_patches[resize_size].save(os.path.join(
                        output_dir, slide_name, resize_sizes_to_path_chunk[resize_size],
                        f"{x}_{y}.png"))

@pytest.mark.parametrize("shuffle", [True, False])
def test_SlidePatchExtractor_resize_sizes(shuffle, mock_slides, output_dir):
    os_slide = mock_slides['TCGA-HNSC-2']
    patch_size = 512
    resize_sizes = [256, 128]
    sce = SlideCoordsExtractor(os_slide, patch_size)
    sce_sorted_result = list(sce)
    spe_result = [ ]
    for patch, tile_loc, resized_patches in SlidePatchExtractor(
            os_slide, patch_size, resize_sizes=resize_sizes, shuffle=shuffle):
        tile_x, tile_y, x, y = tile_loc
        spe_result.append(tile_loc)
        assert almost_zero(utils.image.rmsdiff(patch, resized_patches[patch_size]))
        resized_patches[patch_size].save(os.path.join(output_dir,
                f"{patch_size}_{x}_{y}.png"))
        resized_patches[resize_sizes[0]].save(os.path.join(output_dir,
                f"{resize_sizes[0]}_{x}_{y}.png"))
        resized_patches[resize_sizes[1]].save(os.path.join(output_dir,
                f"{resize_sizes[1]}_{x}_{y}.png"))
    if shuffle:
        assert spe_result != sce_sorted_result 
        assert sorted(spe_result, key=lambda x: (x[1]*10000) + x[0]) \
                == sce_sorted_result
    else:
        assert spe_result == sce_sorted_result 
    for file in os.listdir(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2']):
        expected_patchpath = os.path.join(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2'], file)
        expected_patch = Image.open(expected_patchpath)
        actual_patchpath = os.path.join(output_dir, f"{patch_size}_{file}")
        actual_patch = Image.open(actual_patchpath)
        assert almost_zero(utils.image.rmsdiff(expected_patch, actual_patch))
        
    for file in os.listdir(MOCK_PATCHES_256_20_DIR['TCGA-HNSC-2']):
        expected_patchpath = os.path.join(MOCK_PATCHES_256_20_DIR['TCGA-HNSC-2'], file)
        expected_patch = Image.open(expected_patchpath)
        actual_patchpath = os.path.join(output_dir, f"{resize_sizes[0]}_{file}")
        actual_patch = Image.open(actual_patchpath)
        assert almost_zero(utils.image.rmsdiff(expected_patch, actual_patch))

    for file in os.listdir(MOCK_PATCHES_128_10_DIR['TCGA-HNSC-2']):
        expected_patchpath = os.path.join(MOCK_PATCHES_128_10_DIR['TCGA-HNSC-2'], file)
        expected_patch = Image.open(expected_patchpath)
        actual_patchpath = os.path.join(output_dir, f"{resize_sizes[1]}_{file}")
        actual_patch = Image.open(actual_patchpath)
        assert almost_zero(utils.image.rmsdiff(expected_patch, actual_patch))

def test_SlidePatchExtractor_shuffle(mock_slides, output_dir):
    """
    TODO: 
    """
    os_slide = mock_slides['TCGA-HNSC-2']
    patch_size = 512
    sce = SlideCoordsExtractor(os_slide, patch_size)
    sce_sorted_result = list(sce)
    spe_result = [ ]
    for patch, tile_loc, resized_patches in SlidePatchExtractor(
                os_slide, patch_size, shuffle=True):
        tile_x, tile_y, x, y = tile_loc
        spe_result.append(tile_loc)
        assert patch.size == (patch_size, patch_size,)
        assert almost_zero(utils.image.rmsdiff(patch, resized_patches[patch_size]))
        patch.save(os.path.join(output_dir, f"{x}_{y}.png"))
    assert spe_result != sce_sorted_result 
    assert sorted(spe_result, key=lambda x: (x[1]*10000) + x[0]) \
            == sce_sorted_result
    for file in os.listdir(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2']):
        expected_patchpath = os.path.join(MOCK_PATCHES_512_40_DIR['TCGA-HNSC-2'], file)
        expected_patch = Image.open(expected_patchpath)
        actual_patchpath = os.path.join(output_dir, file)
        actual_patch = Image.open(actual_patchpath)
        assert almost_zero(utils.image.rmsdiff(expected_patch, actual_patch))

