import json
import collections

class CoordsMetadata(collections.abc.Iterable):
    """Coordinate metadata of patches extracted from a slide.
    """

    def __init__(self, slide_name, coords={}, patch_size=1024):
        """Initialized

        Parameters
        ----------
        slide_name : str
            Name of extracted slide.

        coords : dict of (str: list of collection)
            Labeled (x, y) coordinates of top left corner of patches in slide.
        
        patch_size : int
            Pixel size of extracted patch from slide.
        """
        self.slide_name = slide_name
        self.coords = coords
        self.patch_size = patch_size
    
    @property
    def labels(self):
        return self.coords.keys()
    
    def add_coord(self, label, x, y):
        if label not in self.coords:
            self.coords[label] = []
        self.coords[label].append((x, y,))

    def get_topleft_coords(self, label):
        """Get coordinates of top left corner of patches that are labeled with label in slide.

        Parameters
        ----------
        label : str
            The label of the patches to get top left corner coordinates from.
        
        Returns
        -------
        iterable of (tuple of int)
            List of x, y coordinates of top left corner of patches.
        """
        return map(lambda coord: tuple(coord), self.coords[label]) 

    def __iter__(self):
        """Generate a list of coordinates of top left corner of patches, and the label of the coordinates.

        Returns
        -------
        generator of tuple
            Generator of label and (x, y) coordinate of top left corner of patches.
        """
        for label, coord_seq in self.coords.items():
            for coordinate in coord_seq:
                yield (label, tuple(coordinate),)


class SlideCoordsMetadata(object):
    """Represents a slide coords manifest.
    This manifest records the coordinates of each patch extracted from each slide.

    SlideCoordsMetadata saves/load slide coordinates JSON file with the format specified by SLIDE_COORDS_METADATA below.

    ```
    PATCH_SIZE := integer of size of patch of PATCH_SIZE x PATCH_SIZE to extract from every slide.
    RESIZE_SIZES := list of integer of sizes to downsample extracted patch to RESIZE_SIZES x RESIZE_SIZES patch and save.
    REGION_LABEL := key specifying region annotation label the list value of coordinates belong to.
    COORDINATE := list [x, y] of 2 integers specifying top-left corner of extracted patch.
    SLIDE_COORDS_METADATA := {
        patch_size: [[ PATCH_SIZE ]],
        resize_sizes: [[ RESIZE_SIZES ]],
        slides: {
            [[ slide ID ]]: {
                [[ REGION_LABEL ]]: [
                    [[ COORDINATE ]]
                ],
                ...
            },
            ...
        }
    }
    ```

    Attributes
    ----------
    slide_coords_file : str
    
    slides : dict of (str: CoordsMetadata)
        JSON persistable state of slide-coords manifest.
    """

    @classmethod
    def load(cls, slide_coords_file):
        slide_coords = cls(slide_coords_file)
        with open(slide_coords.slide_coords_file, 'r') as f:
            metadata = json.load(f)
        slide_coords.patch_size = metadata['patch_size']
        if 'resize_sizes' in metadata:
            slide_coords.resize_sizes = metadata['resize_sizes']
        for slide_name, coords in metadata['slides'].items():
            slide_coords.slides[slide_name] = CoordsMetadata(slide_name,
                    coords=coords, patch_size=slide_coords.patch_size)
        return slide_coords

    def __init__(self, slide_coords_file,
            patch_size=1024, resize_sizes=[]):
        self.slide_coords_file = slide_coords_file
        self.slides = { }
        self.patch_size = patch_size
        self.__resize_sizes = resize_sizes
        self.augment_metadata = None

    @property
    def slide_names(self):
        return self.slides.keys()
    
    @property
    def resize_sizes(self):
        if self.__resize_sizes:
            return self.__resize_sizes
        else:
            return [self.patch_size]
    
    @resize_sizes.setter
    def resize_sizes(self, resize_sizes):
        self.__resize_sizes = resize_sizes
    
    def has_slide(self, slide_name):
        return slide_name in self.slides

    def get_slide(self, slide_name):
        """

        Parameters
        ----------
        slide_name
            Slide name to search by

        Returns
        -------
        CoordsMetadata
            Coordinate metadata of slide with slide name
        """
        return self.slides[slide_name]

    def consume_coords(self, coords):
        """Add the coordinates of slides to metadata.

        Parameters
        ----------
        coords : CoordsMetadata or (list of CoordsMetadata)
            The slide coords to add.

        Invariant
        ---------
        Assumes slide not been added yet.
        """
        if isinstance(coords, list):
            for sing_coords in coords:
                if sing_coords.slide_name in self.slides:
                    raise ValueError(
                            f"{sing_coords.slide_name} should not already be in slides "
                            "coords metadata.")
                if sing_coords.patch_size != self.patch_size:
                    raise ValueError(
                            f"patch sizes {sing_coords.patch_size} and "
                            f"{self.patch_size} ""do not match")
                self.slides[sing_coords.slide_name] = sing_coords
        else:
            if coords.slide_name in self.slides:
                raise ValueError(
                        f"{sing_coords.slide_name} should not already be in slides "
                        "coords metadata.")
            if coords.patch_size != self.patch_size:
                raise ValueError(
                        f"patch sizes {coords.patch_size} and {self.patch_size} do not "
                        "match")
            self.slides[coords.slide_name] = coords

    def dump(self):
        metadata = { }
        metadata['patch_size'] = self.patch_size
        if self.__resize_sizes:
            metadata['resize_sizes'] = self.__resize_sizes
        metadata['slides'] = { }
        for slide_name, coords in self.slides.items():
            metadata['slides'][slide_name] = { }
            for label in coords.labels:
                metadata['slides'][slide_name][label] \
                        = list(coords.get_topleft_coords(label))
        return metadata

    def save(self):
        """Save slide_coords dict to JSON file at slide_coords_file
        """
        with open(self.slide_coords_file, 'w') as f:
            json.dump(self.dump(), f)
