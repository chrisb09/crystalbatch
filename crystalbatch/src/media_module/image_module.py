from media_module import MediaModule
import media_module

class ImageModule(MediaModule):

    def get_file_extensions(self):
        return ["png","jpg","jpeg","bmp","gif"]
 
    def get_module_name(self):
        return "Image"
 
    def get_module_description(self):
        return "Display all sort of image files including animated gifs."
 
    def check_requirements(self):
        return False
 
    def render(self):
        pass

    def update_window_size(self):
        pass

media_module.media_modules.append(ImageModule())