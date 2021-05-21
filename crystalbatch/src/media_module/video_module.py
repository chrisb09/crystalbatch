from media_module import PlayableMediaModule
import media_module

class VideoModule(PlayableMediaModule):

    def get_file_extensions(self):
        return ["mp4","webm","avi","mkv"]
 
    def get_module_name(self):
        return "Video"
 
    def get_module_description(self):
        return "Display all sort of video files using gstreamer. Installing gstreamer is required."
 
    def check_requirements(self):
        return False
 
    def render(self):
        pass

    def update_window_size(self):
        pass
 
    def toggle_pause_resume(self):
        pass
 
    def forward(self):
        pass
 
    def rewind(self):
        pass

media_module.media_modules.append(VideoModule())