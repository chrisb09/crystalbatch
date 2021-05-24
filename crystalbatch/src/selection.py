# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from functools import partial

from . import language


def callback_folder_select(entry):
    res = filedialog.askdirectory(mustexist=True)
    if str == type(res) and len(res) > 0:
        entry.delete(0, END)
        entry.insert(0, res)


# Source: https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind("<Configure>", _configure_canvas)


window = tk.Tk()
window.title("Crystal batch file renamer")
# window.wm_attributes('-type', 'splash')
# window.configure(background='red')


window.tk.call("wm", "iconphoto", window._w, tk.PhotoImage(file="logos/Crystal_focus_color.png"))

window.minsize(window.winfo_screenwidth() // 2, window.winfo_screenheight() // 2)

# top_text.pack()


# label = Label(text="Shrink the window to activate the scrollbar.")
# label.pack()

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=2)
window.grid_columnconfigure(1, weight=1)

window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=20)
window.grid_rowconfigure(2, weight=3)

top_text = Message(window, text=language.translation_json["Content"]["select_source_target_pairs"], fg="black", justify="center")
top_text.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=NSEW)
top_text.bind("<Configure>", lambda e: top_text.configure(width=window.winfo_width()-10))

settings_frame = LabelFrame(window, text="Settings", bd=5, relief=RIDGE)
settings_frame.grid(row=1, column=0, padx=20, pady=20, sticky=NSEW)

pairing_frame = LabelFrame(window, text="Pairings", bd=5, relief=RIDGE)
pairing_frame.grid(row=1, column=1, sticky=NSEW, padx=20, pady=20)

frame = VerticalScrolledFrame(pairing_frame)
# frame.interior.configure(background='red')
frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
# frame.pack()
pair_frames = []
for i in range(5):
    pair_frames.append(LabelFrame(frame.interior, text="Pair #"+str(i+1), bd=5, relief=RIDGE))
    pair_frames[-1].pack(side=TOP, fill=X, expand=TRUE, padx=20, pady=10)

    pair_frames[-1].grid_columnconfigure(0, weight=1)
    pair_frames[-1].grid_columnconfigure(1, weight=2)
    pair_frames[-1].grid_columnconfigure(1, weight=1)

    pair_frames[-1].grid_rowconfigure(0, weight=1)
    pair_frames[-1].grid_rowconfigure(1, weight=1)
    pair_frames[-1].grid_rowconfigure(2, weight=1)

    Label(pair_frames[-1], text=language.translation_json["Content"]["source_dir"]+":").grid(row=0, column=0, padx=5, pady=5, sticky=E)
    source_entry = Entry(pair_frames[-1], fg="black", bg="white", justify="left")
    source_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky=EW)
    Button(
        pair_frames[-1],
        text="...",
        command=partial(callback_folder_select, source_entry),
    ).grid(row=0, column=2, columnspan=1, padx=0, pady=5, sticky=E)
    Label(pair_frames[-1], text=language.translation_json["Content"]["target_dir"]+":").grid(row=1, column=0, padx=5, pady=5, sticky=E)
    target_entry = Entry(pair_frames[-1], fg="black", bg="white", justify="left")
    target_entry.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky=EW)
    Button(
        pair_frames[-1],
        text="...",
        command=partial(callback_folder_select, target_entry),
    ).grid(row=1, column=2, columnspan=1, padx=0, pady=5, sticky=E)


window.mainloop()
