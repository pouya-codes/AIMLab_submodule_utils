import h5py, glob
import torch
import cv2
import os
from PIL import Image
from torchvision.transforms import ToTensor
from submodule_utils import *
from openslide import OpenSlide
from tqdm import tqdm
from pytorch_grad_cam.grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

class GradCAM_AIM():

    """Creating the gradcam activation map as a hd5 file.

    The generated hd5 file has the below structure:

    ```
    Dataset hierarchy: {patch_size}/{magnification}/grad_cam, image_coordinates, slide_diminsions
    Dataset data: {patch_size}/{magnification}/grad_cam is a tile_x in tile_y array that contains a 32X32 activation map for each patch
    Dataset data: {patch_size}/{magnification}/image_coordinates is a string that contains the tiles of the patches that we have generated acitvation map for. 
    Dataset data: {patch_size}/{magnification}/slide_diminsions contains (width, height) of the slide
    ```

    """


    def get_tile_dimensions(self, os_slide, patch_size):
        width, height = os_slide.dimensions
        return int(width / patch_size), int(height / patch_size), width, height


    def create_hdf_datasets(self, hdf, os_slide, patch_size, magnification):
        tile_width, tile_height, width, height = self.get_tile_dimensions(os_slide, patch_size * int(40 // magnification))
        group_name = "{}/{}".format(patch_size, magnification)
        group = hdf.require_group(group_name)
        datasets = {}
        datasets["grad_cam"] = group.create_dataset("grad_cam",
                                                    (tile_height, tile_width, 32, 32),
                                                     compression="gzip", compression_opts=9, dtype='f')
        datasets["image_coordinates"] = group.create_dataset("image_coordinates", (1, ), dtype=h5py.special_dtype(vlen=str))
        datasets["slide_diminsions"] = group.create_dataset("slide_diminsions", (2, ), dtype='f')
        datasets["slide_diminsions"][0] = width
        datasets["slide_diminsions"][1] = height
        return datasets

    def get_gradcam(self, patch_paths, cur_datas, gt_label):

        grayscale_cam = self.gradcam(input_tensor=cur_datas, target_category=gt_label)
        for patch_path, cam in zip(patch_paths, grayscale_cam):

            patch_id = create_patch_id(patch_path, self.patch_pattern)
            patch_size = get_patch_size_by_patch_id(patch_id, self.patch_pattern)
            slide_id = get_slide_by_patch_id(patch_id, self.patch_pattern)
            

            # save overlayed gradcam and patch images
            if not self.generate_gradcam_h5:

                os.makedirs(f"{self.gradcam_location}/{slide_id}", exist_ok=True)

                rgb_img = cv2.imread(patch_path, 1)[:, :, ::-1]
                rgb_img = cv2.resize(rgb_img, (patch_size, patch_size))
                rgb_img = np.float32(rgb_img) / 255
                file_name = patch_id.split("/")[-1] + ".png"
                
                cam_image = show_cam_on_image(rgb_img, cam) 
                cv2.imwrite(f"{self.gradcam_location}/{slide_id}/{file_name}", cam_image)

            # save the overlay gradcam activation map as a hd5 file
            else :
                cam = cv2.resize(cam, (32, 32)) # downsample activation map
                magnification = get_magnification_by_patch_id(patch_id, self.patch_pattern)
                tile_y, tile_x = get_patch_tile_by_patch_id(patch_id, patch_size * int(40 // magnification))

                # for each patch store the activation map in the dataset
                if slide_id in self.dict_gradcams: 
                    self.dict_gradcams[slide_id]['meta']['image_coordinates'] += f"{tile_x}_{tile_y}-"
                    
                else:
                    self.dict_gradcams[slide_id] = {'meta': {'patch_size': patch_size,'magnification': magnification,
                                                    'image_coordinates': f"{tile_x}_{tile_y}-"}, 'data': []}
                self.dict_gradcams[slide_id]['data'].append([tile_x, tile_y, cam])
        

    def save_gradcam_h5(self):

        out_path = f"{self.gradcam_location}/grad_cam_h5_files"

        print ("Creating h5 activation maps ...")
        for slide_id in tqdm(self.dict_gradcams.keys()):

            try:
                slide_path = glob.glob(f"{os.path.join(self.slides_path, slide_id)}.*")[0]
                os_slide = OpenSlide(slide_path)
            except:
                print(f"could not find/open {slide_id} at {self.slides_path}")
                continue

            hdf = h5py.File(f"{out_path}/{slide_id}.h5", 'w')

            datasets = self.create_hdf_datasets(hdf, os_slide, self.dict_gradcams[slide_id]['meta']['patch_size'],
                                         self.dict_gradcams[slide_id]['meta']['magnification'])

            
            for tile_x, tile_y, grad_cam in self.dict_gradcams[slide_id]['data']:
                datasets["grad_cam"][tile_x, tile_y] = grad_cam
            datasets["image_coordinates"][0] = self.dict_gradcams[slide_id]['meta']['image_coordinates']
            
            print (f"created {slide_id} h5 activation map.")


    def __init__(self, slides_path, category_enum, patch_pattern, gradcam_location, deep_model, gradcam_h5):
        """

        """
        self.slides_path = slides_path
        self.category_enum = category_enum
        self.patch_pattern = patch_pattern
        self.gradcam_location = gradcam_location
        self.layer = [deep_model.feature_extract[-1]]
        self.gradcam = GradCAM(model=deep_model, target_layers=self.layer, use_cuda=torch.cuda.is_available())
        self.generate_gradcam_h5 = gradcam_h5

        if (self.generate_gradcam_h5):
            self.dict_gradcams = {}
            os.makedirs(f"{self.gradcam_location}/grad_cam_h5_files", exist_ok=True)
            




