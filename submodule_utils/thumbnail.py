import os

import submodule_utils as utils
import cv2
import numpy as np
from PIL import Image

class PlotThumbnail(object):
    def __init__(self, slide_name, os_slide, hd5_file_path, annotation=None, mask=None):
        """
        Parameters
        ----------
        os_slide : OpenSlide

        hd5_file_path : str

        annotation : dict

        """
        self.os_slide = os_slide
        self.hd5_file_path = hd5_file_path
        self.annotation = annotation
        self.mask = mask
        self.slide_name = slide_name
        self.store_path = os.path.join(os.path.dirname(self.hd5_file_path),
                                       'Thumbnails')
        # Get maximum downsample and minimum dimension
        self.down_sample = self.os_slide.level_downsamples[-1]
        self.dimensions  = self.os_slide.level_dimensions[-1]
        self.run()

    def get_thumbnail(self):
        thumbnail = self.os_slide.get_thumbnail(self.dimensions)
        self.thumbnail = cv2.cvtColor(np.array(thumbnail), cv2.COLOR_RGB2BGR)

        # thumbnail.save(f'thumbnail_slide_{slide_name}.png')

    def draw_annotation(self):
        if self.annotation is not None:
            overlay = self.thumbnail.copy()
            poly = self.annotation.polygons
            alpha = 0.2 # that's the transparency factor
            for label, polygons in poly.items():
                if label=='Tumor': color=(0, 0, 255) # Red # color=(0, 255, 255) # Yellow
                elif label=='Stroma' or label=='Necrosis': color=(0, 255, 0) # Green # color=(255, 255, 0) # Cyan / Aqua
                else: color=(192,192,192) # Silver
                for polygon in polygons:
                    int_coords = lambda x: (np.array(x)/self.down_sample).round().astype(np.int32)
                    if polygon.type=='Polygon':
                        # draw a line
                        exterior = int_coords(polygon.exterior.coords)
                        xs, ys = exterior[:,0], exterior[:,1]
                        draw_points = (np.asarray([xs, ys]).T).astype(np.int32)
                        cv2.polylines(self.thumbnail, [draw_points], False, color, 2)
                        # draw a polygon
                        # exterior = [int_coords(polygon.exterior.coords)]
                        # cv2.fillPoly(overlay, exterior, color=color)
                    else:
                        for polygon_ in polygon:

                            # draw a line
                            exterior = int_coords(polygon_.exterior.coords)
                            xs, ys = exterior[:,0], exterior[:,1]
                            draw_points = (np.asarray([xs, ys]).T).astype(np.int32)
                            cv2.polylines(self.thumbnail, [draw_points], False, color, 2)
                            # draw a polygon
                            # exterior = [int_coords(polygon_.exterior.coords)]
                            # cv2.fillPoly(overlay, exterior, color=color)
            # draw a polygon
            # cv2.addWeighted(overlay, alpha, self.thumbnail, 1 - alpha, 0, self.thumbnail)

    def draw_mask(self):
        if self.mask is not None:
            overlay = self.thumbnail.copy()
            poly = self.mask.polygons
            alpha = 0.3 # that's the transparency factor
            for polygons in poly.values():
                color=(100, 100, 100)
                for polygon in polygons:
                    int_coords = lambda x: (np.array(x)/self.down_sample).round().astype(np.int32)
                    if polygon.type=='Polygon':
                        # draw a line
                        exterior = int_coords(polygon.exterior.coords)
                        xs, ys = exterior[:,0], exterior[:,1]
                        draw_points = (np.asarray([xs, ys]).T).astype(np.int32)
                        cv2.polylines(self.thumbnail, [draw_points], False, color, 2)
                        # draw a polygon
                        # exterior = [int_coords(polygon.exterior.coords)]
                        # cv2.fillPoly(overlay, exterior, color=color)
                    else:
                        for polygon_ in polygon:
                            # draw a line
                            exterior = int_coords(polygon_.exterior.coords)
                            xs, ys = exterior[:,0], exterior[:,1]
                            draw_points = (np.asarray([xs, ys]).T).astype(np.int32)
                            cv2.polylines(self.thumbnail, [draw_points], False, color, 2)
                            # draw a polygon
                            # exterior = [int_coords(polygon_.exterior.coords)]
                            # cv2.fillPoly(overlay, exterior, color=color)
            # draw a polygon
            # cv2.addWeighted(overlay, alpha, self.thumbnail, 1 - alpha, 0, self.thumbnail)

    def draw_patches(self):
        paths, patch_size = utils.open_hd5_file(self.hd5_file_path)
        for path in paths:
            (x,  y ) = os.path.splitext(os.path.basename(path))[0].split('_')
            # resize_size = int(utils.get_patchsize_by_patch_path(path))
            (x,  y ) = (int(x),  int(y))
            # (x_, y_) = (x+resize_size, y+resize_size)
            (x_, y_) = (x+patch_size, y+patch_size)
            (x,  y ) = (int(x/self.down_sample), int(y/self.down_sample))
            (x_, y_) = (int(x_/self.down_sample), int(y_/self.down_sample))
            cv2.rectangle(self.thumbnail, (x, y), (x_, y_), (255,0,0), 2)

    def save_thumbnail(self):
        self.thumbnail = Image.fromarray(cv2.cvtColor(self.thumbnail, cv2.COLOR_BGR2RGB))
        self.thumbnail.save(f'{os.path.join(self.store_path, self.slide_name)}.png')

    def run(self):
        os.makedirs(self.store_path, exist_ok=True)
        self.get_thumbnail()
        self.draw_annotation()
        self.draw_mask()
        self.draw_patches()
        self.save_thumbnail()
