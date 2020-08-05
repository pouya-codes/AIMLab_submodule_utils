
import pytest
import pandas as pd

import submodule_utils as utils
from submodule_utils.mixins import OutputMixin

def print_outputs(outputs):
    for k1, v1 in outputs.items():
        print(k1)
        if isinstance(v1, dict):
            for k2, v2 in v1.items():
                print(f"    {k2}")
                print(v2.to_markdown())
        else:
            print(v1.to_markdown())
        print()

class MockOutputs(OutputMixin):
    def __init__(self, patch_pattern, dataset_origin, subtypes=None, is_binary=None):
        self.is_binary = is_binary
        self.patch_pattern = utils.create_patch_pattern(patch_pattern)
        self.CategoryEnum = utils.create_category_enum(is_binary, subtypes)
        self.dataset_origin = dataset_origin

"""Test 2 groups for Tumor / Normal
Group 1: (unique patient) patches
Group 2: (unique patient) patches
"""
groups_OUT_1 = {'chunks': [
    {'id': 0, 'imgs': [
        '/path/to/Tumor/MMRd/VOA-1001A/256/10/0.png',
        '/path/to/Tumor/MMRd/VOA-1002B/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-1003C/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-1004D/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-1005E/256/10/0.png',
    ]},
    {'id': 1, 'imgs': [
        '/path/to/Tumor/MMRd/VOA-2001A/256/10/0.png',
        '/path/to/Tumor/MMRd/VOA-2002B/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-2003C/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-2004D/256/10/0.png',
    ]},
]}
is_binary_OUT_1 = True
patch_pattern_OUT_1 = 'annotation/subtype/slide/patch_size/magnification'
subtypes_OUT_1 = {'MMRD':0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
dataset_origin_OUT_1 = 'ovcare'
patient_patches_Group_1_OUT_1 = pd.DataFrame({
    'Normal': [0, 0, 1, 1, 1, 3],
    'Tumor': [1, 1, 0, 0, 0, 2],
    'Overall': [1, 1, 1, 1, 1, 5],
},
        dtype=pd.Int64Dtype,
        index=utils.map_to_list(str, [1001, 1002, 1003, 1004, 1005, 'Total']))
patient_patches_Group_2_OUT_1 = pd.DataFrame({
    'Normal': [0, 0, 1, 1, 2],
    'Tumor': [1, 1, 0, 0, 2],
    'Overall': [1, 1, 1, 1, 4],
},
        dtype=pd.Int64Dtype,
        index=utils.map_to_list(str, [2001, 2002, 2003, 2004, 'Total']))
group_asterix_OUT_1 = pd.DataFrame({
    'Normal': [3, 2, 5],
    'Tumor': [2, 2, 4],
    'Overall': [5, 4, 9],
},
        dtype=pd.Int64Dtype,
        index=['Group 1', 'Group 2', 'Total'])
expected_OUT_1 = {
    'patient_patches': {
        'Group 1': patient_patches_Group_1_OUT_1,
        'Group 2': patient_patches_Group_2_OUT_1,
    },
    'group_patches': group_asterix_OUT_1,
    'group_slides': group_asterix_OUT_1,
    'group_patients': group_asterix_OUT_1,
}

"""Test 2 groups for Tumor / Normal
Group 1: (overlapping patient, unique slide) patches
Group 2: (overlapping slide, unique patch ID) patches
Group 3: (unique / overlapping patient, slide) patches
"""
groups_OUT_3 = {'chunks': [
    {'id': 0, 'imgs': [
        '/path/to/Tumor/MMRd/VOA-1001A/256/10/0.png',
        '/path/to/Tumor/MMRd/VOA-1001B/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-1001C/256/10/0.png',
        '/path/to/Tumor/MMRd/VOA-1002A/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-1002B/256/10/0.png',
    ]},
    {'id': 1, 'imgs': [
        '/path/to/Tumor/MMRd/VOA-2001A/256/10/0.png',
        '/path/to/Tumor/MMRd/VOA-2001A/256/10/1.png',
        '/path/to/Stroma/MMRd/VOA-2001A/256/10/2.png',
        '/path/to/Tumor/MMRd/VOA-2002A/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-2002A/256/10/1.png',
        '/path/to/Stroma/MMRd/VOA-2002A/256/10/2.png',
    ]},
    {'id': 2, 'imgs': [
        '/path/to/Stroma/MMRd/VOA-3001A/256/10/0.png',
        '/path/to/Stroma/MMRd/VOA-3001A/256/10/1.png',
        '/path/to/Stroma/MMRd/VOA-3001B/256/10/2.png',
        '/path/to/Stroma/MMRd/VOA-3001C/256/10/3.png',
        '/path/to/Stroma/MMRd/VOA-4001A/256/10/4.png',
        '/path/to/Stroma/MMRd/VOA-4001A/256/10/5.png',
    ]},
]}
is_binary_OUT_3 = True
patch_pattern_OUT_3 = 'annotation/subtype/slide/patch_size/magnification'
subtypes_OUT_3 = {'MMRD':0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
dataset_origin_OUT_3 = 'ovcare'
patient_patches_Group_1_OUT_3 = pd.DataFrame({
    'Normal': [1, 1, 2],
    'Tumor': [2, 1, 3],
    'Overall': [3, 2, 5],
},
        dtype=pd.Int64Dtype,
        index=utils.map_to_list(str, [1001, 1002, 'Total']))
patient_patches_Group_2_OUT_3 = pd.DataFrame({
    'Normal': [1, 2, 3],
    'Tumor': [2, 1, 3],
    'Overall': [3, 3, 6],
},
        dtype=pd.Int64Dtype,
        index=utils.map_to_list(str, [2001, 2002, 'Total']))
patient_patches_Group_3_OUT_3 = pd.DataFrame({
    'Normal': [4, 2, 6],
    'Tumor': [0, 0, 0],
    'Overall': [4, 2, 6],
},
        dtype=pd.Int64Dtype,
        index=utils.map_to_list(str, [3001, 4001, 'Total']))
group_patches_OUT_3 = pd.DataFrame({
        'Normal': [2, 3, 6, 11],
        'Tumor': [3, 3, 0, 6],
        'Overall': [5, 6, 6, 17],
},
        dtype=pd.Int64Dtype,
        index=['Group 1', 'Group 2', 'Group 3', 'Total'])
group_slides_OUT_3 = pd.DataFrame({
        'Normal': [2, 2, 4, 8],
        'Tumor': [3, 2, 0, 5],
        'Overall': [5, 2, 4, 11],
},
        dtype=pd.Int64Dtype,
        index=['Group 1', 'Group 2', 'Group 3', 'Total'])
group_patients_OUT_3 = pd.DataFrame({
        'Normal': [2, 2, 2, 6],
        'Tumor': [2, 2, 0, 4],
        'Overall': [2, 2, 2, 6],
},
        dtype=pd.Int64Dtype,
        index=['Group 1', 'Group 2', 'Group 3', 'Total'])

expected_OUT_3 = {
    'patient_patches': {
        'Group 1': patient_patches_Group_1_OUT_3,
        'Group 2': patient_patches_Group_2_OUT_3,
        'Group 3': patient_patches_Group_3_OUT_3,
    },
    'group_patches': group_patches_OUT_3,
    'group_slides': group_slides_OUT_3,
    'group_patients': group_patients_OUT_3,
}

TEST_PARAMETERS = [
    pytest.param(is_binary_OUT_1, patch_pattern_OUT_1, subtypes_OUT_1,
            dataset_origin_OUT_1, groups_OUT_1, expected_OUT_1, id='OUT_1'),
    pytest.param(is_binary_OUT_3, patch_pattern_OUT_3, subtypes_OUT_3,
            dataset_origin_OUT_3, groups_OUT_3, expected_OUT_3, id='OUT_3'),
]

@pytest.mark.parametrize(
        "is_binary,patch_pattern,subtypes,dataset_origin,groups,expected",
        TEST_PARAMETERS)
def test_output_mixin(is_binary, patch_pattern, subtypes, dataset_origin,
        groups, expected):
    outputs_maker = MockOutputs(patch_pattern, dataset_origin, subtypes, is_binary)
    modified_groups = outputs_maker.generate_group_summary_table(groups)

    # print_outputs(modified_groups)
    for group_id, tally in modified_groups['patient_patches'].items():
        pd.testing.assert_frame_equal(tally,
                expected['patient_patches'][group_id])
    pd.testing.assert_frame_equal(
            modified_groups['group_patches'],
            expected['group_patches'])
    pd.testing.assert_frame_equal(
            modified_groups['group_slides'],
            expected['group_slides'])
    pd.testing.assert_frame_equal(
            modified_groups['group_patients'],
            expected['group_patients'])

@pytest.mark.parametrize(
        "is_binary,patch_pattern,subtypes,dataset_origin,groups,expected",
        TEST_PARAMETERS)
def test_generate_output(is_binary, patch_pattern, subtypes, dataset_origin,
        groups, expected):
    outputs_maker = MockOutputs(patch_pattern, dataset_origin, subtypes, is_binary)
    modified_groups = outputs_maker.print_group_summary(groups)
    # modified_groups = outputs_maker.generate_group_summary_table(groups)
    # print_outputs(modified_groups)
