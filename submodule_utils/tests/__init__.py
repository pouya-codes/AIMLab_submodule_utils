import os

OUTPUT_DIR = 'submodule_utils/tests/outputs'
MOCK_DATASET_DIR = 'submodule_utils/tests/mock/datasets/test_dataset_1'
MOCK_SLIDES_DIR = os.path.join(MOCK_DATASET_DIR, 'slides')
MOCK_PATCHES_512_40_DIR = {
    'TCGA-HNSC-2': os.path.join(MOCK_DATASET_DIR,
            'patches/TCGA-HNSC-2/512/40')
}
MOCK_PATCHES_256_20_DIR = {
    'TCGA-HNSC-2': os.path.join(MOCK_DATASET_DIR,
            'patches/TCGA-HNSC-2/256/20')
}
MOCK_PATCHES_128_10_DIR = {
    'TCGA-HNSC-2': os.path.join(MOCK_DATASET_DIR,
            'patches/TCGA-HNSC-2/128/10')
}
ERR_THRESHOLD = 8e-3