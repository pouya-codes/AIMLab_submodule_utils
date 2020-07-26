#!/bin/bash
#SBATCH --job-name test
#SBATCH --cpus-per-task 6
#SBATCH --output /projects/ovcare/classification/cchen/ml/slurm/test.%j.out
#SBATCH --error  /projects/ovcare/classification/cchen/ml/slurm/test.%j.out
#SBATCH -w {w}
#SBATCH -p {p}
#SBATCH --gres=gpu:1
#SBATCH --time=3-00:00:00
#SBATCH --chdir /projects/ovcare/classification/cchen/ml/submodule_utils
#SBATCH --mem=70G

DLHOST04_SINGULARITY=/opt/singularity-3.4.0/bin
if [[ -d "$DLHOST04_SINGULARITY" ]]; then
    PATH="{$PATH}:{$DLHOST04_SINGULARITY}"
fi
if [[ -d /projects/ovcare/classification/cchen ]]; then
    cd /projects/ovcare/classification/cchen/ml/submodule_utils
    source /projects/ovcare/classification/cchen/{pyenv}
fi

if [[ ! -d submodule_utils/tests/mock ]]; then
    tar xvzf submodule_utils/tests/mock.tar.gz -C submodule_utils/tests/
fi

mkdir -p submodule_utils/tests/outputs
# pytest -s -vv submodule_utils/tests/test_manifest_arguments.py
# pytest -s -vv submodule_utils/tests/test_metadata.py
pytest -s -vv submodule_utils/tests/test_image_extract.py::test_SlidePatchExtractor_to_generate
# pytest -s -vv submodule_utils/tests/
