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

    @classmethod
    def get_vertices(cls, line):
        """Get region segment vertices from a line in annotation TXT
        """
        xy = [float(s) for s in re.findall(cls.POINT_REGEX, line)]
        return [[x,y] for x, y in zip(xy[::2], xy[1::2])]

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

    def __init__(self, annotation_file, overlap_threshold=1.0, logger=None):
        """
        Parameters
        ----------
        annotation_file : str
            Path to annotation TXT file

        """
        self.slide_name = utils.path_to_filename(annotation_file)
        self.annotation_file = annotation_file
        if logger:
            self.logger = logger
        self.overlap_threshold = overlap_threshold
        if self.overlap_threshold > 1.0:
            raise ValueError("overlap_threshold should be less than 1!")
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
        if self.overlap_threshold==1:
            for label, paths in self.paths.items():
                for path in paths:
                    if np.sum(path.contains_points(points)) == 4:
                        return label
        else:
            # Check the ratio of overlapping area
            patch = shapely.geometry.Polygon(points)
            for label, polygons in self.polygons.items():
                for polygon in polygons:
                    intersection = patch.intersection(polygon)
                    percent_area = intersection.area / patch.area
                    if percent_area >= self.overlap_threshold:
                        return label
        return None
