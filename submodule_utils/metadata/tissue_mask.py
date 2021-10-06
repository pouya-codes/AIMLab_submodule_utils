import os
import os.path
import re
import cv2
import numpy as np
import matplotlib
import matplotlib.path
import shapely
import shapely.geometry
import shapely

import submodule_utils as utils

class TissueMask(object):
    POINT_REGEX = re.compile(r"-?\d+\.?\d*")

    @classmethod
    def get_label(cls, line):
        """Get region label from a line in annotation TXT
        """
        return line.split('[')[0].strip()

    def get_vertices(self, line):
        """Get region segment vertices from a line in annotation TXT
        """
        xy = [float(s) for s in re.findall(self.POINT_REGEX, line)]
        vertices = [[x,y] for x, y in zip(xy[::2], xy[1::2])]
        return vertices

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

    def __init__(self, mask_file, mask_overlap, patch_size, slide_size):
        """
        Parameters
        ----------
        mask_file : str
            Path to mask png or txt file

        patch_size : int
            The size of the patch to extract.

        mask_overlap : float

        slide_size : tuple
        """
        self.slide_name = utils.path_to_filename(mask_file)
        self.mask_file = mask_file
        self.mask_overlap = mask_overlap
        self.patch_size = patch_size
        self.slide_size = slide_size
        self.__set_up()

    def __set_up(self):
        """
        Returns
        -------
        dict of matplotlib.path.Path
        """
        self.polygons = {'clean_area': []}
        if self.mask_file.endswith(".txt"):
            with open(self.mask_file, 'r') as f:
                for line in f:
                    if line != '':
                        label = self.get_label(line)
                        if label != 'clean_area':
                            raise ValueError(f'The only accepted label is clean_area '
                                             f'but the label is {label}')
                        if len(label) != 0:
                            vertices = self.get_vertices(line)
                            self.polygons[label].append(self.get_polygon(vertices))
        elif self.mask_file.endswith(".png") or self.mask_file.endswith(".svs"):
            mask = cv2.imread(self.mask_file, cv2.IMREAD_GRAYSCALE)
            ratio_width = round(self.slide_size[0] / mask.shape[1])
            ratio_heigh = round(self.slide_size[1] / mask.shape[0])
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            polygon = None
            for contour in contours:
                points = contour.reshape(-1,2)
                # scale points
                points[:, 0] *= ratio_width
                points[:, 1] *= ratio_heigh
                points_list = points.tolist()
                if len(points_list) < 3:
                    continue
                poly = shapely.geometry.Polygon(points_list)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                if polygon is None:
                    polygon = poly
                else:
                    polygon = polygon.union(poly)
            if polygon.type=='Polygon':
                self.polygons['clean_area'] = [polygon]
            else:
                self.polygons['clean_area'] = list(polygon)
        else:
            raise NotImplementedError(f'Only .txt, and .png and .svs files are supported for the masks.')

    def get_area(self, factor=1.0):
        return {label: factor * self.count_polygons_area(polygons) \
                for label, polygons in self.polygons.items()}

    @property
    def labels(self):
        return self.polygons.keys()

    def points_to_label(self, points):
        """Get label of region that contains all the points, or return None if points are not in any region.
        """
        # Check the ratio of overlapping area
        patch = shapely.geometry.Polygon(points)
        area_ = 0
        for label, polygons in self.polygons.items():
            for polygon in polygons:
                intersection = patch.intersection(polygon)
                percent_area = intersection.area / patch.area
                if percent_area >= self.mask_overlap:
                    return label
                if area_ >= self.mask_overlap: # if total of overlaps reach that criteria
                    return label
                area_ += percent_area
        return None
