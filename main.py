
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import random, sys, os, shutil
from threading import Thread, Lock
import time
import hashlib

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstAudio', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, GLib
from gi.repository import GdkX11, GstVideo
#import gst, gobject

TITLE_HEIGHT = 100
LOWER_BAR_HEIGHT = 100
VIDEO_FILE_EXTENSIONS = set([".mkv", ".mp4", ".avi", ".webm"])
IMAGE_FILE_EXTENSIONS = set([".png", ".jpg", ".jpeg", ".gif", ".bmp"])

#Read all words listed in the words.txt file
def read_words():
    dirname = os.path.dirname(__file__)
    text_file = open(os.path.join(dirname, "res/txt/words.txt"), "r", encoding='utf-8', errors='ignore')
    lines = text_file.readlines()
    wordlists = lines
    return wordlists

#Heuristic to evaluate a text(filename) of a program and determine if it consists of actual words
def get_score(text):
    global words
    wordscore = 0
    for word in words:
        w = word.rstrip()
        if w in text:
            wordscore += len(w)*len(w)
    return int(100*wordscore/(max(len(text)**(1.41),1)))

#get the next entry in the queue (list of image files that remain in the source folder)
def next_entry():
    global file_index
    global files
    if file_index < len(files):
        set_image(files[file_index][0])
        file_index += 1
    else:
        print("Done.")
        exit()

#try to properly split the filename for display in the top bar
def split_text_after_max(text, n):
    parts_reversed = []
    delimiters = set([" ", "    "])
    delimiters_weak_pre = set(["[","{","<"])
    delimiters_weak_suf = set(["]","}",">", "-", "_", ":", "|", "="])
    i = len(text) - n
    max_l = len(text)
    while i < len(text) and i > 0:
        if text[i] in delimiters:
            parts_reversed.append(text[i+1:])
            text = text[:i]
            i = len(text)-n
        elif text[i] in delimiters_weak_pre:
            parts_reversed.append(text[i:])
            text = text[:i]
            i = len(text)-n
        elif text[i] in delimiters_weak_suf:
            parts_reversed.append(text[i+1:])
            text = text[:i+1]
            i = len(text)-n
        i += 1
    parts_reversed.append(text)
    parts = []
    for i in range(len(parts_reversed)-1,-1,-1):
        parts.append(parts_reversed[i])
    return "\n".join(parts)

#update the filename shown in the top bar for the file given in 'path'
def update_top_bar_filename(path):
    if limit[0] <= 1:
        return
    base = os.path.basename(path)
    file_name, _ = os.path.splitext(base)
    word_score = get_score(file_name)
    color_score = 255 * word_score // (word_score + 300)
    label.config(bg=_from_rgb((255-color_score,color_score,64)))
    init_fs = 32
    chars_per_line = (limit[0]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))/init_fs
    line_inc_char_rate = 2
    line_amount_req = 1
    print(file_name)
    while line_amount_req * chars_per_line * line_inc_char_rate**(line_amount_req-1) < len(file_name):
        line_amount_req += 1
    fs = int(init_fs/line_amount_req)
    label.config(font=("Courier",  fs))
    file_name_adjusted = split_text_after_max(file_name, int(chars_per_line * line_inc_char_rate**(line_amount_req-1)))
    label.config(text=file_name_adjusted)

class VideoThread(Thread):
    loop = None

    def __init__(self):
        Thread.__init__(self)
        print("")
        self.loop = GLib.MainLoop()

    def run(self):
        self.loop.run()

    def stop(self):
        self.loop.quit()


class GifThread(Thread):

  gif_path = None
  index = 0
  stop = False
  image_object = None
  next_frame_timestamp = 0

  def __init__(self, path):
    Thread.__init__(self)
    self.gif_path = path
    if path.lower().endswith(".gif"):
        self.image_object = Image.open(path)
        global video_paused
        video_paused = False
        if not self.image_object.is_animated:
            self.stop = True
    else:
        self.stop = True

  def run(self):
    global limit, image, video_paused

    while self.stop == False:
        current = self.image_object.size
        factor = min(limit[0]/current[0],(limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT) )/current[1])
        self.image_object.seek(self.index%self.image_object.n_frames)
        logo = ImageTk.PhotoImage(self.image_object.resize((int(current[0]*factor), int(current[1]*factor)), Image.ANTIALIAS))
        now = time.time()
        while video_paused:
            time.sleep(1/60)
        if self.next_frame_timestamp > now:
            time.sleep(self.next_frame_timestamp-now)
        self.next_frame_timestamp = now + self.image_object.info['duration'] / 1000.0
        if self.stop == False:
            image.config(image=logo)
            image.image = logo
            #perhaps more action is needed
            self.index = self.index + 1

def stop_gif_thread():
    global gif_thread
    if gif_thread is not None:
        if gif_thread.is_alive():
            gif_thread.stop = True
        gif_thread = None

def stop_video():
    global video_player, video_thread
    if video_player is not None:
        video_player.set_state(Gst.State.NULL)
    if video_thread is not None:
        if video_thread.is_alive():
            video_thread.stop()

def toggle_pause_video():
    global video_player, video_paused
    if video_player is not None: # or video_player.get_state() == Gst.State.NULL:
        if video_paused:
            video_player.set_state(Gst.State.PLAYING)
            print("Play")
        else:
            video_player.set_state(Gst.State.PAUSED)
            print("Resume")
    video_paused = not video_paused


#def on_sync_message(bus, message, window_id):
#    if not message.structure is None:
#        if message.structure.get_name() == 'prepare-xwindow-id':
#            image_sink = message.src
#            image_sink.set_property('force-aspect-ratio', True)
#            image_sink.set_xwindow_id(window_id)

def on_eos(bus, message):
    print("EOS")

def on_message(bus, message):
    global video_player, video_paused
    t = message.type
    if t == Gst.MessageType.EOS:
        video_player.set_state(Gst.State.NULL)
        print("STOP")
        video_paused = True
        video_player.set_state(Gst.State.PLAYING)
        video_paused = False
    elif t == Gst.MessageType.ERROR:
        video_player.set_state(Gst.State.NULL)
        err, debug = message.parse_error()
        print("Error: " + err)
        print("Debug: " + debug)
        video_paused = True

def on_sync_message(bus, message, window_id):
    #print(message.get_structure().get_name())
    if message.get_structure().get_name() == 'prepare-window-handle':
        imagesink = message.src
        imagesink.set_property("force-aspect-ratio", True)
        imagesink.set_window_handle(window_id)

#update the image shown in the application
def set_image(path):
    if path is None:
        return
    global limit, image, gif_thread, last_path, video_paused
    print("Open '"+path+"'")
    _, file_extension = os.path.splitext(path)
    if file_extension.lower() in IMAGE_FILE_EXTENSIONS:
        stop_video()
        print("Image...")
        image_f = Image.open(path)
        current = image_f.size
        factor = min(limit[0]/current[0],(limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT) )/current[1])
        logo = ImageTk.PhotoImage(image_f.resize((int(current[0]*factor), int(current[1]*factor)), Image.ANTIALIAS))
        image.config(image=logo)
        image.image = logo
        center_window.place_forget()
        center_window.place(x=0,y=TITLE_HEIGHT,width=limit[0],height=limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))
        image.place_forget()
        image.place(x=(limit[0]-int(current[0]*factor))//2,
            y=0+(((limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))- int(current[1]*factor))//2),
            width=int(current[0]*factor), height=int(current[1]*factor))
        if gif_thread is None or gif_thread.is_alive() == False or gif_thread.gif_path is None or not gif_thread.gif_path == path:
            gif_thread = GifThread(path)
            gif_thread.start()
    elif file_extension.lower() in VIDEO_FILE_EXTENSIONS:
        print("Video...")
        center_window.place_forget()
        center_window.place(x=0,y=TITLE_HEIGHT,width=limit[0],height=limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))
        if last_path is None or not last_path == path:
            stop_video()
            image.place_forget()
            window_id = center_window.winfo_id()

            global video_thread
            #if video_thread is None:
            video_thread = VideoThread()
            video_thread.start()
            #video_panel = Frame(window, bg='#000000')
            #video_panel.pack(side=tk.BOTTOM,anchor=tk.S,expand=tk.YES,fill=tk.BOTH)

            #video_panel.place_forget()
            #video_panel.place(x=0,y=TITLE_HEIGHT,width=limit[0],height=limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))

            #window_id = video_panel.winfo_id()

            #player = gst.element_factory_make('playbin2', 'player')
            player = Gst.ElementFactory.make('playbin', 'player')
            player.set_property('video-sink', None)
            player.set_property('uri', 'file://%s' % (os.path.abspath(path)))
            player.set_state(Gst.State.PLAYING)
            global video_player, video_paused
            video_player = player
            video_paused = False

            bus = player.get_bus()
            bus.add_signal_watch()
            bus.connect("message", on_message)
            bus.connect("message::eos", on_eos)
            bus.enable_sync_message_emission()
            bus.connect('sync-message::element', on_sync_message, window_id)

    update_top_bar_filename(path)
    last_path = path


#delete the currently shown file
def delete_file():
    global files, file_index
    path = files[file_index-1][0]
    os.remove(path)

#move the currently shown file and rename it if a new name has been entered
def move_file(name_entered):
    global files, file_index
    path = files[file_index-1][0]
    target = files[file_index-1][1]
    base = os.path.basename(path)
    new_filename = None

    if len(name_entered) == 0:
        new_filename = base
    else:
        _, file_extension = os.path.splitext(base)
        new_filename = name_entered + file_extension
    _save_move(path, os.path.join(target,new_filename))

#move a file in a way that duplicates are avoided by adding a number in brackets at the end of the name
def _save_move(source, target, number=0):
    target_path = target
    if number != 0:
        path, file_extension = os.path.splitext(target)
        target_path = path + " ("+str(number)+")"+file_extension
    if os.path.exists(target_path):
        _save_move(source, target, number+1)
    else:
        shutil.move(source, target_path)


#Main program start, check if arguments are correct, load words and content of source folder

args = sys.argv
if len(args) < 3:
    print(args[0]+" <source> <target>")
    print("Alternatively: ")
    print(args[0]+" [--source=<source>, ...] [--target=<target>, ...]")
    exit()

sources = []
targets = []

if args[1].startswith("--"):
    for i in range(1,len(args)):
        if args[i].startswith("--source="):
            sources.append(args[i][9:])
        elif args[i].startswith("--target="):
            targets.append(args[i][9:])
        else:
            print("Unknown parameter: "+args[i])
            exit()

else:
    sources.append(os.path.abspath(args[1]))
    targets.append(os.path.abspath(args[2]))

for source in sources:
    if not os.path.exists(source):
        print("Source("+source+") does not exist!")
        exit()

for target in targets:
    if not os.path.exists(target):
        print("Target("+target+") does not exist!")
        exit()

if len(sources) != len(targets):
    print("The amount of source and target folders has to be the same!")
    exit()

if len(sources) == 0:
    print("Please provide a source and target folder")
    exit()

words = read_words()

files = [] #(sourcefile, targetdir)
for i in range(len(sources)):
    source = sources[i]
    for (dirpath, _, filenames) in os.walk(source):
        for filename in filenames:
            #if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".gif") or filename.endswith(".bmp"):
            _, file_extension = os.path.splitext(filename)
            if file_extension.lower() in IMAGE_FILE_EXTENSIONS or file_extension.lower() in VIDEO_FILE_EXTENSIONS:
                files.append((os.path.join(dirpath, filename), targets[i]))

#files.sort(key=lambda x: zlib.adler32(bytes(os.path.basename(x[0]), "utf-8")))
files.sort(key=lambda x: int.from_bytes(hashlib.md5(bytes(os.path.basename(x[0]), "utf-8")).digest(), "big"))

print("Size of queue: "+str(len(files)))

for f in files:
    #print(str(zlib.adler32(bytes(os.path.basename(f[0]), "utf-8"))) + " '"+os.path.basename(f[0])+"' "+ str(f))
    print(str(int.from_bytes(hashlib.md5(bytes(os.path.basename(f[0]), "utf-8")).digest(), "big")) + " '"+os.path.basename(f[0])+"' "+ str(f))

def space(event):
    text = entry.get()
    if text == " " or text == "":
        entry.delete(0,END)
        toggle_pause_video()

def left(event):
    text = entry.get()
    if text == " " or text == "":
        rewind()

def right(event):
    text = entry.get()
    if text == " " or text == "":
        forward()

def rewind():
    rc, pos_int = video_player.query_position(Gst.Format.TIME)
    seek_ns = pos_int - 5 * 1000000000
    if seek_ns < 0:
        seek_ns = 0
    print('Backward: %d ns -> %d ns' % (pos_int, seek_ns))
    video_player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)

def forward():
    rc, pos_int = video_player.query_position(Gst.Format.TIME)
    seek_ns = pos_int + 5 * 1000000000
    print('Forward: %d ns -> %d ns' % (pos_int, seek_ns))
    video_player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)

#register the press of the enter key, rename file and load the next one
def enter(event):
    stop_gif_thread()
    stop_video()
    text = entry.get()
    text = text.replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
    move_file(text)
    next_entry()
    reset_name()

#register the press of the f11 key, toggle fullscreen
def f11(event):
    global limit, fullscreen, window
    fullscreen = not fullscreen
    window.attributes("-fullscreen", fullscreen)

#register the press of the delete key, delete image and load the next one
def delete(event):
    stop_video()
    stop_gif_thread()
    delete_file()
    next_entry()
    reset_name()

#register the press of the escape key, close the window
def quit_window(event):
    global window
    stop_video()
    stop_gif_thread()
    window.destroy()

def mouse_click(event):
    toggle_pause_video()


#register a change to window size and reconfigure window so it scales properly
def configure_event(event):
    global limit, window, label, button_f11, framebottom, button_delete, entry, button_enter
    if limit[0] != window.winfo_width() or limit[1] != window.winfo_height():
        print(str(limit)+" -> " + str((window.winfo_width(), window.winfo_height())))
        limit = (window.winfo_width(), window.winfo_height())
        #title
        label.place_forget()
        label.place(x=TITLE_HEIGHT,y=0,width=limit[0]-2*TITLE_HEIGHT,height=TITLE_HEIGHT)
        button_f11.place_forget()
        button_f11.place(x=limit[0]-TITLE_HEIGHT, y=0, width=TITLE_HEIGHT, height=TITLE_HEIGHT)

        #image
        set_image(files[file_index-1][0])

        #bottom    
        button_delete.place_forget()
        button_delete.place(x=0, y=0, width=LOWER_BAR_HEIGHT, height=LOWER_BAR_HEIGHT)
        entry.place_forget()
        entry.place(x = LOWER_BAR_HEIGHT, y = 0, width=limit[0]-2*LOWER_BAR_HEIGHT, height=LOWER_BAR_HEIGHT)
        button_enter.place_forget()
        button_enter.place(x=limit[0]-LOWER_BAR_HEIGHT, y=0, width=LOWER_BAR_HEIGHT, height=LOWER_BAR_HEIGHT)
        framebottom.place_forget()
        framebottom.place(x=0,y=limit[1]-LOWER_BAR_HEIGHT, width=limit[0], height=LOWER_BAR_HEIGHT)


#translates an rgb tuple of int to a tkinter friendly color code
def _from_rgb(rgb):
    return "#%02x%02x%02x" % rgb   

#create the window and bind the keys to their respective events
fullscreen = True

Gst.init(None)

window = tk.Tk()
window.title("Manual image renaming gui")
window.tk.call('wm', 'iconphoto', window._w, tk.PhotoImage(file='logo.png'))

limit = (window.winfo_screenwidth(), window.winfo_screenheight())
window.minsize(window.winfo_screenwidth()//2, window.winfo_screenheight()//2)

window.attributes('-fullscreen', True)

window.bind("<Return>", enter)
window.bind("<Delete>", delete)
window.bind("<F11>", f11)
window.bind("<Escape>", quit_window)
window.bind("<space>", space)
window.bind("<Left>", left)
window.bind("<Right>", right)

window.attributes("-fullscreen", True)

last_path = None
gif_thread = None
video_player = None
video_paused = False
video_thread = None

window.bind('<Configure>', configure_event)

escape_b = ImageTk.PhotoImage(Image.open("res/img/escape.png").resize((TITLE_HEIGHT, TITLE_HEIGHT), Image.ANTIALIAS))
button_escape = Button(window,
    text="Escape!",
    width=TITLE_HEIGHT,
    height=TITLE_HEIGHT,
    fg="red",
    image = escape_b
)
button_escape.bind("<Button-1>", quit_window)
button_escape.place(x=0, y=0, width=TITLE_HEIGHT, height=TITLE_HEIGHT)

f11_b = ImageTk.PhotoImage(Image.open("res/img/f11.png").resize((TITLE_HEIGHT, TITLE_HEIGHT), Image.ANTIALIAS))
button_f11 = Button(window,
    text="F11!",
    width=TITLE_HEIGHT,
    height=TITLE_HEIGHT,
    fg="red",
    image = f11_b
)
button_f11.bind("<Button-1>", f11)
button_f11.place(x=limit[0]-TITLE_HEIGHT, y=0, width=TITLE_HEIGHT, height=TITLE_HEIGHT)

label = tk.Label(
    text="Empty...",
    fg="red",
    bg = "white",
    width=100,
    height=2
)

label.config(fg="black")
label.config(font=("Courier", 44))
label.place(x=TITLE_HEIGHT,y=0,width=limit[0]-2*TITLE_HEIGHT,height=TITLE_HEIGHT)

center_window = Frame(window, bg="white")
center_window.place(x=0,y=TITLE_HEIGHT,width=limit[0],height=limit[1]-(TITLE_HEIGHT+LOWER_BAR_HEIGHT))
center_window.bind("<Button-1>", mouse_click)

image = Label(center_window, compound = CENTER, bg="white")
image.place(x=0,y=0)
image.bind("<Button-1>", mouse_click)

framebottom = Frame(window)

delete_b = ImageTk.PhotoImage(Image.open("res/img/delete.png").resize((100, 100), Image.ANTIALIAS))
button_delete = Button(framebottom,
    text="Delete!",
    width=100,
    height=100,
    fg="red",
    image = delete_b
)
button_delete.bind("<Button-1>", delete)
enter_b = ImageTk.PhotoImage(Image.open("res/img/enter.png").resize((100, 100), Image.ANTIALIAS))
button_enter = Button(framebottom,
    text="Enter!",
    width=100,
    height=100,
    fg="red",
    image = enter_b
)
button_enter.bind("<Button-1>", enter)

button_delete.place(x=0, y=0, width=LOWER_BAR_HEIGHT, height=LOWER_BAR_HEIGHT)

entry = Entry(framebottom,fg="black", bg="white", justify='center')
entry.config(font=("Courier", 44))
entry.place(x = LOWER_BAR_HEIGHT,
        y = 0,
        width=limit[0]-2*LOWER_BAR_HEIGHT,
        height=LOWER_BAR_HEIGHT)

button_enter.place(x=limit[0]-LOWER_BAR_HEIGHT, y=0, width=LOWER_BAR_HEIGHT, height=LOWER_BAR_HEIGHT)
framebottom.place(x=0,y=limit[1]-LOWER_BAR_HEIGHT, width=limit[0], height=LOWER_BAR_HEIGHT)

file_index = 0
next_entry()

entry.focus_set()

def reset_name():
    entry.delete(0, tk.END)
    entry.focus_set()

window.mainloop()
print("After mainloop")
print(gif_thread)
print(video_thread)