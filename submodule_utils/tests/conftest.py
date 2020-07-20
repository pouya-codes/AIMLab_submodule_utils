import os
import pytest

from submodule_utils.tests import OUTPUT_DIR

@pytest.fixture
def output_dir():
    """Get the directory to save test outputs. Cleans the output directory before and after each test.
    """
    for file in os.listdir(OUTPUT_DIR):
        os.unlink(os.path.join(OUTPUT_DIR, file))
    yield OUTPUT_DIR
    for file in os.listdir(OUTPUT_DIR):
        os.unlink(os.path.join(OUTPUT_DIR, file))