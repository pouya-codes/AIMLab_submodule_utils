import os
import json
import pytest

from submodule_utils.metadata.slide_coords import (
        CoordsMetadata, SlideCoordsMetadata)

def test_CoordsMetadata():
    slide_name = 'VOA-1000A'
    cm = CoordsMetadata(slide_name)
    coords_expected = {
        'Tumor': list(zip(range(0,100), range(5,105))),
        'Stroma': list(zip(range(100,200), range(150,250))),
        'Necrosis': list(zip(range(130,230), range(0,100))),
    }
    for label, cord_seq in coords_expected.items():
        for x, y in cord_seq:
            cm.add_coord(label, x, y)
    assert cm.slide_name == slide_name
    assert cm.patch_size == 1024
    assert cm.labels == coords_expected.keys()
    assert list(cm.get_topleft_coords('Tumor')) \
            == coords_expected['Tumor']
    assert list(cm.get_topleft_coords('Stroma')) \
            == coords_expected['Stroma']
    assert list(cm.get_topleft_coords('Necrosis')) \
            == coords_expected['Necrosis']
    expected = []
    expected.extend([
            ('Tumor', coord) for coord in coords_expected['Tumor']])
    expected.extend([
            ('Stroma', coord) for coord in coords_expected['Stroma']])
    expected.extend([
            ('Necrosis', coord) for coord in coords_expected['Necrosis']])
    expected.sort()
    actual = list(cm)
    actual.sort()
    assert expected == actual
    assert list(cm.get_topleft_coords('Tumor')) == coords_expected['Tumor']
    assert list(cm.get_topleft_coords('Stroma')) == coords_expected['Stroma']
    assert list(cm.get_topleft_coords('Necrosis')) == coords_expected['Necrosis']

SLIDE_COORDS_MOCK_1 = {
    'patch_size': 512,
    'resize_sizes': [256, 128],
    'slides': {
        'VOA-1000A': {
            'Tumor': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(0,10), range(5,15))],
            'Stroma': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(20,30), range(15,25))],
            'Necrosis': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(12,32), range(10,20))],
        },
        'VOA-2000B': {
            'Stroma': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(102,110), range(302,310))],
        },
        'VOA-3000C': {
            'Tumor': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(22,32), range(1,11))],
            'Immune Cells': [(tile_x * 512, tile_y * 512) for tile_x, tile_y \
                    in zip(range(10,20), range(50,60))],
        }
    }
}
SLIDE_COORDS_MOCK_2 = {
    'patch_size': 2048,
    'slides': {
        'VOA-1000A': {
            'Tumor': [(tile_x * 2048, tile_y * 2048) for tile_x, tile_y \
                    in zip(range(0,10), range(5,15))],
            'Necrosis': [(tile_x * 2048, tile_y * 2048) for tile_x, tile_y \
                    in zip(range(12,32), range(10,20))],
        },
        'VOA-2000B': {
            'Stroma': [(tile_x * 2048, tile_y * 2048) for tile_x, tile_y \
                    in zip(range(102,110), range(302,310))],
        },
        'VOA-3000C': {
            'Tumor': [(tile_x * 2048, tile_y * 2048) for tile_x, tile_y \
                    in zip(range(22,32), range(1,11))],
            'Immune Cells': [(tile_x * 2048, tile_y * 2048) for tile_x, tile_y \
                    in zip(range(10,20), range(50,60))],
        }
    }
}
TEST_PARAMETERS = [
    pytest.param(SLIDE_COORDS_MOCK_1, id="SLIDE_COORDS_MOCK_1"),
    pytest.param(SLIDE_COORDS_MOCK_2, id="SLIDE_COORDS_MOCK_2")
]
@pytest.mark.parametrize("slide_coords_mock", TEST_PARAMETERS)
def test_SlideCoordsMetadata_load(slide_coords_mock, output_dir):
    slide_coords_file = os.path.join(output_dir, 'slide_coords.json')
    with open(slide_coords_file, 'w') as f:
        json.dump(slide_coords_mock, f)
    scm = SlideCoordsMetadata.load(slide_coords_file)
    assert isinstance(scm, SlideCoordsMetadata)
    assert scm.patch_size > 0
    assert scm.patch_size == slide_coords_mock['patch_size']
    if 'resize_sizes' in slide_coords_mock:
        assert scm.resize_sizes == slide_coords_mock['resize_sizes']
    else:
        assert scm.resize_sizes == [slide_coords_mock['patch_size']]
    assert len(scm.slide_names) > 0
    assert sorted(scm.slide_names) == sorted(slide_coords_mock['slides'].keys())
    for slide_name, coords in slide_coords_mock['slides'].items():
        cm = scm.get_slide(slide_name)
        assert isinstance(cm, CoordsMetadata)
        assert cm.slide_name == slide_name
        assert cm.patch_size == scm.patch_size
        assert sorted(cm.labels) == sorted(coords.keys())
        
        for label, coord_seq in coords.items():
            assert len(list(cm.get_topleft_coords(label))) > 0
            assert sorted(cm.get_topleft_coords(label)) == sorted(coord_seq)
        expected = []
        for label in coords.keys():
            expected.extend([(label, coord) for coord in coords[label]])
        expected.sort()
        actual = list(cm)
        actual.sort()
        assert expected == actual

@pytest.mark.parametrize("slide_coords_mock", TEST_PARAMETERS)
def test_SlideCoordsMetadata_load(slide_coords_mock, output_dir):
    slide_coords_file = os.path.join(output_dir, 'slide_coords.json')
    saved_slide_coords_file = os.path.join(output_dir, 'saved_slide_coords.json')
    with open(slide_coords_file, 'w') as f:
        json.dump(slide_coords_mock, f)
    scm = SlideCoordsMetadata.load(slide_coords_file)
    """Save state of SlideCoordsMetadata to different path
    """
    scm.slide_coords_file = saved_slide_coords_file
    scm.save()
    with open(slide_coords_file, 'r') as f1:
        with open(saved_slide_coords_file, 'r') as f2:
            assert f1.read() == f2.read()

@pytest.mark.parametrize("slide_coords_mock", TEST_PARAMETERS)
def test_SlideCoordsMetadata_consume_coords(slide_coords_mock, output_dir):
    slide_coords_file = os.path.join(output_dir, 'slide_coords.json')
    with open(slide_coords_file, 'w') as f:
        json.dump(slide_coords_mock, f)
    patch_size = slide_coords_mock['patch_size']
    if 'resize_sizes' in slide_coords_mock:
        resize_sizes = slide_coords_mock['resize_sizes']
    else:
        resize_sizes = []
    cm_to_merge = []
    for slide_name, coords in slide_coords_mock['slides'].items():
        cm = CoordsMetadata(slide_name, coords=coords, patch_size=patch_size)
        cm_to_merge.append(cm)
    scm_actual = SlideCoordsMetadata(slide_coords_file,
            patch_size=patch_size, resize_sizes=resize_sizes)
    scm_actual.consume_coords(cm_to_merge)
    scm_expected = SlideCoordsMetadata.load(slide_coords_file)
    actual =  json.dumps(scm_actual.dump())
    expected = json.dumps(scm_expected.dump())
    assert actual == expected
