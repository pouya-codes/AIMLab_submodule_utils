import os
import os.path
import re
import numpy as np
import matplotlib
import matplotlib.path
import shapely
import shapely.geometry
import shapely

import submodule_utils as utils

class GroovyAnnotation(object):
    POINT_REGEX = re.compile(r"-?\d+\.?\d*")

    @classmethod
    def get_label(cls, line):
        """Get region label from a line in annotation TXT
        """
        return line.split('[')[0].strip()

    # @classmethod
    # def get_vertices(cls, line):
    #     """Get region segment vertices from a line in annotation TXT
    #     """
    #     xy = [float(s) for s in re.findall(cls.POINT_REGEX, line)]
    #     return [[x,y] for x, y in zip(xy[::2], xy[1::2])]
    def get_vertices(self, line):
        """Get region segment vertices from a line in annotation TXT
        """
        xy = [float(s) for s in re.findall(self.POINT_REGEX, line)]
        if not self.is_TMA:
            vertices = [[x,y] for x, y in zip(xy[::2], xy[1::2])]
        else:
            # if it is TMA, the core has been expanded
            border = int((1+0.3-self.annotation_overlap)*self.patch_size)
            vertices = [[x+border,y+border] for x, y in zip(xy[::2], xy[1::2])]
        return vertices

    @classmethod
    def get_path(cls, vertices):
        """Get single region formed by vertices as matplotlib.path.Path
        """
        return matplotlib.path.Path(vertices,
                closed=True, readonly=True)

    @classmethod
    def get_polygon(cls, vertices):
        """Get single region formed by vertices as shapely.geometry.Polygon
        """
        polygon = shapely.geometry.Polygon(vertices)
        # remove intercross
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        return polygon

    @classmethod
    def count_polygons_area(cls, polygons):
        return sum(map(lambda p: p.area, polygons))

    def __init__(self, annotation_file, annotation_overlap, patch_size, is_TMA, logger=None):
        """
        Parameters
        ----------
        annotation_file : str
            Path to annotation TXT file

        patch_size : int
            The size of the patch to extract.

        annotation_overlap : float

        is_TMA: bool
            it is TMA or not

        logger: logger
            print info

        """
        self.slide_name = utils.path_to_filename(annotation_file)
        self.annotation_file = annotation_file
        if logger:
            self.logger = logger
        self.annotation_overlap = annotation_overlap
        self.patch_size = patch_size
        self.is_TMA = is_TMA
        if self.annotation_overlap > 1.0:
            raise ValueError("annotation_overlap should be less than 1!")
        self.__set_up()

    def __set_up(self):
        """
        Returns
        -------
        dict of matplotlib.path.Path
        """
        self.paths = {}
        self.polygons = {}
        with open(self.annotation_file, 'r') as f:
            for line in f:
                if line != '':
                    label = self.get_label(line)
                    if len(label) != 0:
                        if label not in self.paths:
                            self.paths[label] = []
                        if label not in self.polygons:
                            self.polygons[label] = []
                        vertices = self.get_vertices(line)
                        self.paths[label].append(self.get_path(vertices))
                        self.polygons[label].append(self.get_polygon(vertices))
                    else:
                        if self.logger:
                            self.logger.info(f"Slide {self.slide_name} has annotation(label) without name.")

    def get_area(self, factor=1.0):
        return {label: factor * self.count_polygons_area(polygons) \
                for label, polygons in self.polygons.items()}

    @property
    def labels(self):
        return self.paths.keys()


    def points_to_label(self, points):
        """Get label of region that contains all the points, or return None if points are not in any region.
        """
        labels = []
        if self.annotation_overlap==1:
            for label, paths in self.paths.items():
                for path in paths:
                    if np.sum(path.contains_points(points)) == 4:
                        labels.append(label)
            return labels
        else:
            # Check the ratio of overlapping area
            patch = shapely.geometry.Polygon(points)
            for label, polygons in self.polygons.items():
                for polygon in polygons:
                    intersection = patch.intersection(polygon)
                    percent_area = intersection.area / patch.area
                    if percent_area >= self.annotation_overlap:
                        labels.append(label)
            return labels
        return None
