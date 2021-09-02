import os
import cv2
import numpy as np
from PIL import Image
import submodule_utils as utils
from shapely.geometry import Polygon
from submodule_utils.metadata.annotation import GroovyAnnotation


class FakeAnnotation(object):
    """
    Important Note:
    x, y are coordinates in PIL image format.
    The difference between CV2 and PIL is:
        Output of PIL is w, h
        Output of CV2 is h, w, 3
    Therefore, x and y in PIL is y and x in CV2.

    but in image we first use column then row which is opposite of the way we handle matrix

    therefore using x and y in PIL format while using cv2 library is fine and correct!
    """

    def __init__(self, slide_name, os_slide, annotation_file_path, magnification, patch_size, skip_area):
        """
        Parameters
        ----------
        os_slide : OpenSlide

        hd5_file_path : str

        annotation : dict

        """
        self.patch_size = patch_size
        self.os_slide = os_slide
        self.annotation_file_path = annotation_file_path
        self.slide_name = slide_name
        self.store_path = os.path.join(os.path.dirname(self.annotation_file_path),
                                       'Annotation')
        self.store_thubmnail_path = os.path.join(self.store_path, 'Thumbnail')
        self.annotation_file = os.path.join(self.store_path, f'{self.slide_name}.txt')
        self.multi_poly = None
        self.skip_area = skip_area

    def add_poly(self, x, y):
        coords = [(x, y), (x+self.patch_size, y),
                  (x+self.patch_size, y+self.patch_size), (x, y+self.patch_size)]
        poly = Polygon(coords)

        if self.multi_poly is None:
            self.multi_poly = poly
        else:
            self.multi_poly = self.multi_poly.union(poly)

    def thumbnail_(self):
        # Get maximum downsample and minimum dimension
        self.down_sample = self.os_slide.level_downsamples[-1]
        self.dimensions  = self.os_slide.level_dimensions[-1]

        self.annotation = GroovyAnnotation(self.annotation_file, 0, 0, False, None)

        def get_thumbnail():
            thumbnail = self.os_slide.get_thumbnail(self.dimensions)
            self.thumbnail = cv2.cvtColor(np.array(thumbnail), cv2.COLOR_RGB2BGR)

        def save_thumbnail():
            self.thumbnail = Image.fromarray(cv2.cvtColor(self.thumbnail, cv2.COLOR_BGR2RGB))
            self.thumbnail.save(f'{os.path.join(self.store_thubmnail_path, self.slide_name)}.png')

        def draw_annotation():
            overlay = self.thumbnail.copy()
            poly = self.annotation.polygons
            alpha = 0.2 # that's the transparency factor
            for label, polygons in poly.items():
                if label=='Tumor': color=(0, 0, 255) # Red # color=(0, 255, 255) # Yellow
                elif label=='Stroma' or label=='Necrosis': color=(0, 255, 0) # Green # color=(255, 255, 0) # Cyan / Aqua
                else: color=(192,192,192) # Silver
                for polygon in polygons:
                    int_coords = lambda x: (np.array(x)/self.down_sample).round().astype(np.int32)
                    # draw a line
                    exterior = int_coords(polygon.exterior.coords)
                    xs, ys = exterior[:,0], exterior[:,1]
                    draw_points = (np.asarray([xs, ys]).T).astype(np.int32)
                    cv2.polylines(self.thumbnail, [draw_points], False, color, 2)
                    # draw a polygon
                    # exterior = [int_coords(polygon.exterior.coords)]
                    # cv2.fillPoly(overlay, exterior, color=color)
            # cv2.addWeighted(overlay, alpha, self.thumbnail, 1 - alpha, 0, self.thumbnail)

        get_thumbnail()
        draw_annotation()
        save_thumbnail()

    def save_to_txt_file(self):
        file = open(self.annotation_file, "w")
        label = 'Tumor'
        if self.multi_poly.type=='Polygon':
            self.multi_poly = [self.multi_poly]
        else:
            self.multi_poly = list(self.multi_poly)
        for poly in self.multi_poly:
            if self.skip_area is not None:
                if int(poly.area) <= self.skip_area:
                    continue
            line = ''
            line += label
            line += ' ['
            x, y = poly.exterior.coords.xy
            for x_, y_ in zip(x, y):
                line += f"Point: {x_}, {y_}, "
            line = line[:-2] + ']\n'
            file.write(line)
        file.close()

    def run(self):
        os.makedirs(self.store_path, exist_ok=True)
        os.makedirs(self.store_thubmnail_path, exist_ok=True)
        self.save_to_txt_file()
        self.thumbnail_()
