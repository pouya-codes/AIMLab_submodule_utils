import h5py, csv, glob
from submodule_utils import *
from openslide import OpenSlide

def get_list_from_probability_string(orig_string):
    """probability has form "[0.333 0.666]", for example. It is type str."""
    new_list = []
    for num in orig_string[1:-1].split(' '):
        try:
            new_list.append(float(num))
        except:
            pass
    return new_list


def get_tile_dimensions(os_slide, patch_size):
    width, height = os_slide.dimensions
    return int(width / patch_size), int(height / patch_size)


def create_hdf_datasets(hdf, os_slide, patch_size, magnification, CategoryEnum):
    tile_width, tile_height = get_tile_dimensions(os_slide, patch_size)
    group_name = "{}/{}".format(patch_size, magnification)
    group = hdf.require_group(group_name)
    datasets = {}
    for c in CategoryEnum:
        if c.name in group:
            del group[c.name]
        datasets[c.name] = group.create_dataset(c.name,
                                                (tile_height, tile_width,), dtype='f')
    return datasets


def generate_heatmaps(csv_path, patch_pattern, CategoryEnum, slides_path, heatmap_location):
    reader = csv.reader(open(csv_path))
    slides = {}
    for idx, line in enumerate(reader):
        if idx < 1:
            continue
        file_name, predicted_label, real_label, probability, _ = line
        patch_pattern = create_patch_pattern(patch_pattern)
        patch_id = create_patch_id(file_name, patch_pattern)
        slide_id = get_slide_by_patch_id(patch_id, patch_pattern)
        patch_size = get_patch_size_by_patch_id(patch_id, patch_pattern)

        tile_y, tile_x = get_patch_tile_by_patch_id(patch_id, patch_size)
        probabilities = get_list_from_probability_string(probability)
        if slide_id in slides:
            slides[slide_id]['data'].append([tile_x, tile_y, probabilities])
        else:
            slides[slide_id] = {'meta': {'magnification': get_magnification_by_patch_id(patch_id, patch_pattern),
                                         'patch_size': patch_size},
                                'data': []}

    for key, value in slides.items():
        heatmap_filepath = os.path.join(heatmap_location, f'heatmap.0.{key}.h5')
        hdf = h5py.File(heatmap_filepath, 'w')
        try:
            slide_path = glob.glob(f"{os.path.join(slides_path, key)}.*")[0]
            os_slide = OpenSlide(slide_path)
        except:
            print(f"could not find/open {key} at {slides_path}")
            continue

        datasets = create_hdf_datasets(hdf, os_slide, slides[key]['meta']['patch_size'],
                                       slides[key]['meta']['magnification'], CategoryEnum)

        for record in slides[key]['data']:
            for idx, c in enumerate(CategoryEnum):
                datasets[c.name][record[0], record[1]] = record[2][idx]


