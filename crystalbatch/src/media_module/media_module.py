from abc import ABC, abstractmethod

media_modules = []

class MediaModule(ABC):
 
    @abstractmethod
    def get_file_extensions(self):
        pass
 
    @abstractmethod
    def get_module_name(self):
        pass
 
    @abstractmethod
    def get_module_description(self):
        pass
 
    @abstractmethod
    def check_requirements(self):
        pass
 
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def update_window_size(self):
        pass

class PlayableMediaModule(MediaModule):
 
    @abstractmethod
    def toggle_pause_resume(self):
        pass
 
    @abstractmethod
    def forward(self):
        pass
 
    @abstractmethod
    def rewind(self):
        pass