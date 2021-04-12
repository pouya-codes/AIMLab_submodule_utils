import os
import pytest
import unittest
import random
import numpy as np

import submodule_utils as utils

random.seed(256)

class TestUtils(unittest.TestCase):

    def test_MANY(self):
        """Test many small functions
        """
        # test utils.list_to_space_sep_str
        expected = "1 2 3 4 5 6"
        actual  = utils.list_to_space_sep_str([1, 2, 3, 4, 5, 6])
        assert expected == actual

        # test utils.count
        assert 2 == utils.count(lambda x: x == True,
                [True, False, True, False, False])
        
        # test utils.merge_list_of_list
        expected = [1, 2, 3, 4, 5, 6]
        actual = utils.merge_list_of_list([[1, 2], [3, 4], [5, 6]])
        assert expected == actual

        # test utils.get_inner_key_from_dict_of_dict
        d = {
            'a': {
                'a1': 1,
                'a2': 2,
                'a3': 3,
            },
            'b': {
                'b1': 1,
                'b2': 2,
            },
            'c': {
                'c1': 1,
            },
        }
        expected = ['a1', 'a2', 'a3', 'b1', 'b2', 'c1']
        expected.sort()
        inner_keys = utils.get_inner_key_from_dict_of_dict(d)
        assert isinstance(inner_keys, list)
        assert sorted(inner_keys) == expected

    def test_create_patch_id(self):
        path = '/path/to/patch/Tumor/CC/VOA-1234A/1234_5687.png'
        patch_pattern = utils.create_patch_pattern(
                'annotation/subtype/slide')
        patch_id = utils.create_patch_id(path, patch_pattern)
        assert patch_id == 'Tumor/CC/VOA-1234A/1234_5687'
        slide_id = utils.get_slide_by_patch_id(patch_id, patch_pattern)
        assert slide_id == 'VOA-1234A'
        patient_id = utils.get_patient_by_slide_id(slide_id, dataset_origin='ovcare')
        assert patient_id == '1234'
        subtypes={'CC': 0, 'EC': 1, 'HGSC': 2, 'LGSC': 3, 'MC': 4}
        CategoryEnum = utils.create_category_enum(False,
            subtypes=subtypes)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum)
        assert label.name == 'CC'
        CategoryEnum = utils.create_category_enum(True)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum,
                is_binary=True)
        assert label.name == 'Tumor'
    
    def test_create_patch_id_for_tcga(self):
        path = '/path/to/patch/TCGA-A5-A0GH-01Z-00-DX1.22005F4A-0E77-4FCB-B57A-9944866263AE/Necrosis/41984_45056_d_256.png'
        patch_pattern = utils.create_patch_pattern(
                'slide/annotation')
        patch_id = utils.create_patch_id(path, patch_pattern)
        assert patch_id == 'TCGA-A5-A0GH-01Z-00-DX1.22005F4A-0E77-4FCB-B57A-9944866263AE/Necrosis/41984_45056_d_256'
        slide_id = utils.get_slide_by_patch_id(patch_id, patch_pattern)
        assert slide_id == 'TCGA-A5-A0GH-01Z-00-DX1.22005F4A-0E77-4FCB-B57A-9944866263AE'
        patient_id = utils.get_patient_by_slide_id(slide_id, dataset_origin='tcga')
        assert patient_id == 'TCGA-A5-A0GH'
        CategoryEnum = utils.create_category_enum(True)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum,
                is_binary=True)
        assert label.name == 'Normal'

    def test_create_patch_id_for_nonmultiscale(self):
        path = '/path/to/patch/Stroma/LGSC/VOA-1234A/10/1234_5687.png'
        patch_pattern = utils.create_patch_pattern(
                'annotation/subtype/slide/magnification')
        patch_id = utils.create_patch_id(path, patch_pattern)
        assert patch_id == 'Stroma/LGSC/VOA-1234A/10/1234_5687'
        slide_id = utils.get_slide_by_patch_id(patch_id, patch_pattern)
        assert slide_id == 'VOA-1234A'
        patient_id = utils.get_patient_by_slide_id(slide_id, dataset_origin='ovcare')
        assert patient_id == '1234'
        subtypes={'CC': 0, 'EC': 1, 'HGSC': 2, 'LGSC': 3, 'MC': 4}
        CategoryEnum = utils.create_category_enum(False,
            subtypes=subtypes)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum)
        assert label.name == 'LGSC'
        CategoryEnum = utils.create_category_enum(True)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum,
                is_binary=True)
        assert label.name == 'Normal'

    def test_create_patch_id_2(self):
        path = '/path/to/dir/to/patch/Necrosis/VOA-1234A/1234_5687.png'
        patch_pattern = utils.create_patch_pattern(
                'annotation/slide')
        patch_id = utils.create_patch_id(path, patch_pattern)
        assert patch_id == 'Necrosis/VOA-1234A/1234_5687'
        slide_id = utils.get_slide_by_patch_id(patch_id, patch_pattern)
        assert slide_id == 'VOA-1234A'
        patient_id = utils.get_patient_by_slide_id(slide_id, dataset_origin='ovcare')
        assert patient_id == '1234'
        CategoryEnum = utils.create_category_enum(True)
        label = utils.get_label_by_patch_id(patch_id, patch_pattern, CategoryEnum,
                is_binary=True)
        assert label.name == 'Normal'

    def test_create_subtype_patient_slide_patch_dict(self):
        tumor__VOA_1234__VOA_1234A = [
            '/path/to/patch/Tumor/CC/VOA-1234A/0_0.png',
            '/path/to/patch/Tumor/CC/VOA-1234A/1_0.png',
            '/path/to/patch/Tumor/CC/VOA-1234A/2_0.png'
        ]
        normal__VOA_1234__VOA_1234A = [
            '/path/to/patch/Stroma/CC/VOA-1234A/3_0.png',
            '/path/to/patch/Necrosis/CC/VOA-1234A/4_0.png',
            '/path/to/patch/Other/CC/VOA-1234A/5_0.png'
        ]
        tumor__VOA_1234__VOA_1234B = [
            '/path/to/patch/Tumor/CC/VOA-1234B/6_0.png',
            '/path/to/patch/Tumor/CC/VOA-1234B/7_0.png',
            '/path/to/patch/Tumor/CC/VOA-1234B/8_0.png'
        ]
        normal__VOA_1234__VOA_1234B = [
            '/path/to/patch/Stroma/CC/VOA-1234B/9_0.png',
            '/path/to/patch/Necrosis/CC/VOA-1234B/10_0.png',
            '/path/to/patch/Other/CC/VOA-1234B/11_0.png'
        ]
        tumor__VOA_5678__VOA_5678A = [
            '/path/to/patch/Tumor/CC/VOA-5678A/6_0.png',
            '/path/to/patch/Tumor/CC/VOA-5678A/7_0.png',
            '/path/to/patch/Tumor/CC/VOA-5678A/8_0.png'
        ]
        patch_paths = []
        patch_paths.extend(tumor__VOA_1234__VOA_1234A)
        patch_paths.extend(tumor__VOA_1234__VOA_1234B)
        patch_paths.extend(normal__VOA_1234__VOA_1234A)
        patch_paths.extend(tumor__VOA_5678__VOA_5678A)
        patch_paths.extend(normal__VOA_1234__VOA_1234B)
        random.shuffle(patch_paths)
        
        patch_pattern = utils.create_patch_pattern(
                'annotation/subtype/slide')
        CategoryEnum = utils.create_category_enum(True)
        subtype_patient_slide_patch_dict = utils.create_subtype_patient_slide_patch_dict(
                patch_paths, patch_pattern, CategoryEnum, is_binary=True)

        assert set(tumor__VOA_1234__VOA_1234A) == \
                set(subtype_patient_slide_patch_dict['Tumor']['1234']['VOA-1234A'])
        assert set(normal__VOA_1234__VOA_1234A) == \
                set(subtype_patient_slide_patch_dict['Normal']['1234']['VOA-1234A'])
        assert set(tumor__VOA_1234__VOA_1234B) == \
                set(subtype_patient_slide_patch_dict['Tumor']['1234']['VOA-1234B'])
        assert set(normal__VOA_1234__VOA_1234B) == \
                set(subtype_patient_slide_patch_dict['Normal']['1234']['VOA-1234B'])
        assert set(tumor__VOA_5678__VOA_5678A) == \
                set(subtype_patient_slide_patch_dict['Tumor']['5678']['VOA-5678A'])
        
    def test_create_subtype_patient_slide_patch_dict_for_tcga(self):
        tumor__TCGA_PG_A6IB__DX4 = [
            '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Tumor/1_0.png',
            '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Tumor/2_0.png'
        ]
        tumor__TCGA_PG_A6IB__DX1 = [
            '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX1.575AC6BD-6ABA-468D-9A46-DC61BD92269C/Tumor/3_0.png'
        ]
        normal__TCGA_PG_A6IB__DX4 = [
            '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Stroma/2_0.png',
            '/path/to/patch/TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672/Stroma/3_0.png'
        ]
        tumor__TCGA_AX_A1CC__DX2 = [
            '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Tumor/1_0.png',
            '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Tumor/2_0.png'
        ]
        normal__TCGA_AX_A1CC__DX2 = [
            '/path/to/patch/TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1/Necrosis/2_0.png'
        ]
        patch_paths = []
        patch_paths.extend(tumor__TCGA_PG_A6IB__DX4)
        patch_paths.extend(tumor__TCGA_PG_A6IB__DX1)
        patch_paths.extend(normal__TCGA_PG_A6IB__DX4)
        patch_paths.extend(tumor__TCGA_AX_A1CC__DX2)
        patch_paths.extend(normal__TCGA_AX_A1CC__DX2)
        random.shuffle(patch_paths)

        patch_pattern = utils.create_patch_pattern(
                'slide/annotation')
        CategoryEnum = utils.create_category_enum(True)
        subtype_patient_slide_patch_dict = utils.create_subtype_patient_slide_patch_dict(
                patch_paths, patch_pattern, CategoryEnum,
                is_binary=True, dataset_origin='tcga')

        assert set(tumor__TCGA_PG_A6IB__DX4) == \
                set(subtype_patient_slide_patch_dict['Tumor']['TCGA-PG-A6IB']['TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672'])
        assert set(tumor__TCGA_PG_A6IB__DX1) == \
                set(subtype_patient_slide_patch_dict['Tumor']['TCGA-PG-A6IB']['TCGA-PG-A6IB-01Z-00-DX1.575AC6BD-6ABA-468D-9A46-DC61BD92269C'])
        assert set(normal__TCGA_PG_A6IB__DX4) == \
                set(subtype_patient_slide_patch_dict['Normal']['TCGA-PG-A6IB']['TCGA-PG-A6IB-01Z-00-DX4.631A44B6-43E0-4481-AF1F-3EB484784672'])
        assert set(tumor__TCGA_AX_A1CC__DX2) == \
                set(subtype_patient_slide_patch_dict['Tumor']['TCGA-AX-A1CC']['TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1'])
        assert set(normal__TCGA_AX_A1CC__DX2) == \
                set(subtype_patient_slide_patch_dict['Normal']['TCGA-AX-A1CC']['TCGA-AX-A1CC-01Z-00-DX2.9DBD4FAD-5E16-450D-8B8F-CCDD34A211F1'])

    def test_count_subtype(self):
        input_src = [
            '/path/to/patch/Tumor/CC/VOA-1234A/0_0.png',
            '/path/to/patch/Tumor/CC/VOA-1234A/1_0.png',
            '/path/to/patch/Tumor/EC/VOA-1234A/2_0.png',
            '/path/to/patch/Stroma/EC/VOA-5678A/3_0.png',
            '/path/to/patch/Necrosis/HGSC/VOA-5678A/4_0.png',
            '/path/to/patch/Other/HGSC/VOA-5678A/5_0.png',
            '/path/to/patch/MucinousBorderlineTumor/MC/VOA-2000C/6_0.png',
        ]
        subtypes={'CC': 0, 'EC': 1, 'HGSC': 2, 'LGSC': 3, 'MC': 4}
        random.shuffle(input_src)
        patch_pattern = utils.create_patch_pattern(
                'annotation/subtype/slide')
        CategoryEnum = utils.create_category_enum(True,
            subtypes=subtypes)
        count = utils.count_subtype(input_src, patch_pattern, CategoryEnum,
            is_binary=True)
        np.testing.assert_array_equal(count, np.array([4,3]))
        CategoryEnum = utils.create_category_enum(False,
            subtypes=subtypes)
        count = utils.count_subtype(input_src, patch_pattern, CategoryEnum,
            is_binary=False)
        np.testing.assert_array_equal(count, np.array([2,2,2,0,1]))
    
    def test_extract_yaml_from_json(self):
        test_file = "mock/log_local_ec_100_ovr_p53abn_1_20200507-170844.txt"
        test_file = os.path.join(utils.get_dirname_of(__file__), test_file)
        payload = utils.extract_yaml_from_json(test_file)
        assert payload['batch_size'] == 32
        assert payload['chunk_file_location'] == "/projects/ovcare/classification/cchen/ml/data/local_ec_100/splits_subtype_ovr/p53abn_ovr.1_2_train_3_eval.json"
        assert payload['gpu_id'] == None
        assert payload['instance_name'] == "log_local_ec_100_ovr_p53abn_1_20200507-170844"
        assert payload['is_binary'] == False
        assert payload['log_dir_location'] == "/projects/ovcare/classification/cchen/ml/outputs/local_ec_100/logs/test"
        assert payload['log_file_location'] == "/projects/ovcare/classification/cchen/ml/outputs/local_ec_100/logs/train/log_local_ec_100_ovr_p53abn_1_20200507-170844.txt"
        assert payload['model_config_location'] == "/projects/ovcare/classification/cchen/ml/models/config/vgg19_bn__n2__adam__lr_0_0002.json"
        assert payload['model_file_location'] == "/projects/ovcare/classification/cchen/ml/models/local_ec_100/local_ec_100_ovr_p53abn_1_20200507-170844.pth"
        assert payload['num_patch_workers'] == 10
        assert payload['patch_location'] == "/projects/ovcare/classification/cchen/ml/data/local_ec_100/patches_256_sorted_tumor"
        assert payload['patch_pattern'] == "annotation/subtype/slide"
        assert payload['seed'] == 256
        assert payload['subtypes'] == { 'MMRD': 0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3 }
        assert payload['test_chunks'] == [2, 3]
        assert payload['test_shuffle'] == True

    def test_group_ids_1(self):
        patch_pattern = 'annotation/subtype/slide/patch_size/magnification'
        patch_pattern = utils.create_patch_pattern(patch_pattern)
        patch_ids = [
            'Stroma/MMRd/VOA-1000A/512/20/0_0',
            'Stroma/MMRd/VOA-1000A/512/20/2_2',
            'Stroma/MMRd/VOA-1000A/512/10/0_0',
            'Stroma/MMRd/VOA-1000A/256/20/0_0',
            'Stroma/MMRd/VOA-1000A/256/10/0_0',
            'Tumor/POLE/VOA-1000B/256/10/0_0']
        
        actual = utils.group_ids(patch_ids, patch_pattern, include=['patch_size'])
        expected = {
            '512/0_0': [
                'Stroma/MMRd/VOA-1000A/512/20/0_0',
                'Stroma/MMRd/VOA-1000A/512/10/0_0'
            ],
            '512/2_2': [
                'Stroma/MMRd/VOA-1000A/512/20/2_2',
            ],
            '256/0_0': [
                'Stroma/MMRd/VOA-1000A/256/20/0_0',
                'Stroma/MMRd/VOA-1000A/256/10/0_0',
                'Tumor/POLE/VOA-1000B/256/10/0_0'
            ]
        }
        list(map(lambda v: v.sort(), actual.values()))
        list(map(lambda v: v.sort(), expected.values()))
        assert actual == expected
        actual = utils.group_ids(patch_ids, patch_pattern,
                exclude=['patch_size', 'magnification'])
        expected = {
            'Stroma/MMRd/VOA-1000A/0_0': [
                'Stroma/MMRd/VOA-1000A/512/20/0_0',
                'Stroma/MMRd/VOA-1000A/512/10/0_0',
                'Stroma/MMRd/VOA-1000A/256/20/0_0',
                'Stroma/MMRd/VOA-1000A/256/10/0_0'
            ],
            'Stroma/MMRd/VOA-1000A/2_2': [
                'Stroma/MMRd/VOA-1000A/512/20/2_2'
            ],
            'Tumor/POLE/VOA-1000B/0_0': [
                'Tumor/POLE/VOA-1000B/256/10/0_0'
            ]
        }
        list(map(lambda v: v.sort(), actual.values()))
        list(map(lambda v: v.sort(), expected.values()))
        assert actual == expected

    def test_group_paths_1(self):
        patch_pattern = 'annotation/subtype/slide/patch_size/magnification'
        patch_pattern = utils.create_patch_pattern(patch_pattern)
        patch_ids = [
            '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/0_0.png',
            '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/2_2.png',
            '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/10/0_0.png',
            '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/20/0_0.png',
            '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/10/0_0.png',
            '/path/to/rootdir/Tumor/POLE/VOA-1000B/256/10/0_0.png']

        actual = utils.group_paths(patch_ids, patch_pattern, include=['patch_size'])
        # print(actual)
        expected = {
            '512/0_0': [
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/0_0.png',
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/10/0_0.png'
            ],
            '512/2_2': [
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/2_2.png',
            ],
            '256/0_0': [
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/20/0_0.png',
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/10/0_0.png',
                '/path/to/rootdir/Tumor/POLE/VOA-1000B/256/10/0_0.png'
            ]
        }
        list(map(lambda v: v.sort(), actual.values()))
        list(map(lambda v: v.sort(), expected.values()))
        assert actual == expected
        # return
        actual = utils.group_paths(patch_ids, patch_pattern,
                exclude=['patch_size', 'magnification'])
        expected = {
            'Stroma/MMRd/VOA-1000A/0_0': [
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/0_0.png',
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/10/0_0.png',
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/20/0_0.png',
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/256/10/0_0.png'
            ],
            'Stroma/MMRd/VOA-1000A/2_2': [
                '/path/to/rootdir/Stroma/MMRd/VOA-1000A/512/20/2_2.png'
            ],
            'Tumor/POLE/VOA-1000B/0_0': [
                '/path/to/rootdir/Tumor/POLE/VOA-1000B/256/10/0_0.png'
            ]
        }
        list(map(lambda v: v.sort(), actual.values()))
        list(map(lambda v: v.sort(), expected.values()))
        assert actual == expected
