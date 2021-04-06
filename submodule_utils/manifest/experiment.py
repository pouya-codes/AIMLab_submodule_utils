import json

import submodule_utils as utils

class ExperimentManifest(object):
    """Represents a experiment manifest.
    This manifest stores the component arguments to each component.

    Attributes
    ----------
    experiment_file : str
        Path to experiment manifest YAML file.

    store : dict
        YAML persistable state of experiment manifest.
    """

    def __init__(self, experiment_file):
        self.experiment_file = experiment_file
        self.store = utils.load_yaml(self.experiment_file)
    
    def get_component_config(self, component_id):
        return self.store[component_id]
