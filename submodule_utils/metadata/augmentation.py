# Built-in libraries
import json
import collections
import itertools
import logging

# Modules
import submodule_utils as utils

logger = logging.getLogger('utils')

class AugmentPatchesMetadata(collections.abc.Iterable):
    """Metadata containing a list of original patches, augmented patches, and the augmentation steps tacken to create those patches.

    AugmentPatchesMetadata saves/load augmentation recipes JSON file with the format specified by AUGMENTATION_METADATA below.

    ```
    PRE_PATCH_ID := the ID of patch before augmentating.
    POST_PATCH_ID := the ID of patch after an augmentation.
    TYPE := the type of augmentation used at this step of the sequence.
    AUGMENTATION_PARAMETER := key-value pair specifying the parameters used at the augmentation step using the [[ TYPE ]] augmentation in the augment patches component.
    AUGMENTATION_METADATA := {
        patches: {
            [[ PRE_PATCH_ID ]]: {
                [[ POST_PATCH_ID ]]: [
                    {
                        type: TYPE,
                        [[ AUGMENTATION_PARAMETER ]],
                        ...
                    },
                    ...
                ],
                ...
            },
            ...
        }
    }
    ```

    Attributes
    ----------
    augmentation_file : str

    recipes : dict
    """

    @classmethod
    def load(cls, augmentation_file):
        augmentation = cls(augmentation_file)
        with open(augmentation.augmentation_file, 'r') as f:
            metadata = json.load(f)
        augmentation.recipes = metadata['recipes']
        return augmentation

    def __init__(self, augmentation_file):
        self.augmentation_file = augmentation_file
        self.recipes = { }

    def add_recipe(self, pre_patch_id, post_patch_id, recipe):
        """
        pre_patch_id : str
            The ID of patch before augmenting.
        
        post_patch_id : str
            The ID of patch after an augmentation.
        
        recipe : list of dict
            Sequence of steps to take to augment patch with ID pre_patch_id to create patch with ID post_patch_id.
        """
        if pre_patch_id not in self.recipes:
            self.recipes[pre_patch_id] = {}
        if post_patch_id in self.recipes[pre_patch_id]:
            raise ValueError(f"{pre_patch_id} has already been agumented to {post_patch_id} in slides coords metadata.")
        else:
            self.recipes[pre_patch_id][post_patch_id] = recipe

    def __iter__(self):
        """
        Returns
        -------
        generator of tuple
            Generator of recipe tuples to use in augmentation processes. Each recipe tuple contains:
             - pre_patch_id (str) the ID of patch before augmenting.
             - post_patch_id (str) the ID of patch after an augmentation.
             - recipe (list of dict) sequence of steps to take to augment patch with ID pre_patch_id to create patch with ID post_patch_id
        """
        for pre_patch_id, augmentations in self.recipes.items():
            for post_patch_id, recipe in augmentations:
                yield (pre_patch_id, post_patch_id, recipe,)
    
    def __consume_recipe(self, recipes):
        """Add augmentation recipe to metadata.
        
        Parameters
        ----------
        recipes : AugmentPatchesMetadata
            The augmentation recipes to add.
        """
        for pre_patch_id, augmentations in recipes.items():
            if not pre_patch_id in self.recipes:
                self.recipes[pre_patch_id] = { }
            for post_patch_id, recipe in augmentations.items():
                if post_patch_id in self.recipes[pre_patch_id]:
                    raise ValueError(
                            f"Recipe for augment patch {pre_patch_id} to "
                            f"{post_patch_id} is already added.")
                self.recipes[pre_patch_id][post_patch_id] = recipe

    def consume_recipes(self, augmentations):
        """Merge augemntation metadata.
        
        Parameters
        ----------
        augmentation_metadata : AugmentPatchesMetadata or (list of AugmentPatchesMetadata)
            The augmentations to add to this one.
        """
        if not utils.is_iterable(augmentations):
            augmentations = [augmentations]
        recipes = list(map(lambda a: a.recipes, augmentations))
        inner_keys = list(itertools.chain.from_iterable(
                map(utils.get_inner_key_from_dict_of_dict, recipes)))
        len_inner_keys = len(inner_keys)
        inner_keys = set(inner_keys)
        if len(inner_keys) != len_inner_keys:
            raise ValueError(
                    f"There are {len_inner_keys - len(inner_keys)} duplicated IDs of "
                    "augmented patches. Did augmentation process overwrite patches?")
        list(map(self.__consume_recipe, recipes))

    def dump(self):
        metadata = { }
        metadata['recipes'] = self.recipes
        return metadata
    
    def save(self):
        """Save augmentation dict to JSON file at augmentation_file
        """
        with open(self.augmentation_file, 'w') as f:
            json.dump(self.dump(), f)
