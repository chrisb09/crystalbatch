# -*- coding: utf-8 -*-

import os

import tkinter as tk
from tkinter import *
from tkinter import ttk
from functools import partial

from . import language, popup, configuration
from .tooltip import Tooltip


def _write_settings():
    pass


def callback_close_window():
    res = popup.yes_no_cancel(
        language.translation_json["Content"]["quit_title"],
        language.translation_json["Content"]["quit_save_message"],
    )
    # yes=True, no=False, cancel=None
    if res is not None:
        if res:
            _write_settings()
        window.destroy()


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

window.tk.call(
    "wm", "iconphoto", window._w, tk.PhotoImage(file="logos/Crystal_focus_color.png")
)

window.minsize(window.winfo_screenwidth() // 2, window.winfo_screenheight() // 2)

window.protocol("WM_DELETE_WINDOW", callback_close_window)

# top_text.pack()


# label = Label(text="Shrink the window to activate the scrollbar.")
# label.pack()

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=2)
window.grid_columnconfigure(1, weight=1)

window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=20)
window.grid_rowconfigure(2, weight=3)

top_text = Message(
    window,
    text=language.translation_json["Content"]["select_source_target_pairs"],
    fg="black",
    justify="center",
)
top_text.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=NSEW)
top_text.bind(
    "<Configure>", lambda e: top_text.configure(width=window.winfo_width() - 10)
)

settings_frame = LabelFrame(window, text="Settings", bd=5, relief=RIDGE)
settings_frame.grid(row=1, column=0, padx=20, pady=20, sticky=NSEW)

settings_frame.grid_columnconfigure(0, weight=1)
settings_frame.grid_columnconfigure(1, weight=1)
settings_frame.grid_columnconfigure(1, weight=1)

settings_frame.grid_rowconfigure(0, weight=1)
settings_frame.grid_rowconfigure(1, weight=1)
settings_frame.grid_rowconfigure(2, weight=1)


Label(
    settings_frame,
    text=language.translation_json["Content"]["interface_language"] + ":",
).grid(row=0, column=0, padx=5, pady=5, sticky=E)

_translations = language.list_available_translations()
_lang_combo_selection = -1
for index in range(len(_translations)):
    translation = _translations[index]
    if (
        os.path.basename(translation[2])
        == configuration.config.get("General", "selected_translation") + ".json"
    ):
        _lang_combo_selection = index
_language_box = ttk.Combobox(
    settings_frame,
    state="readonly",
    values=[x + " (" + y + ")" for x, y, _ in _translations],
)
Tooltip(
    _language_box,
    text=language.translation_json["Tooltip"]["select_interface_language"],
)
_language_box.current(_lang_combo_selection)
_language_box.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=EW)

pairing_frame = LabelFrame(window, text="Pairings", bd=5, relief=RIDGE)
pairing_frame.grid(row=1, column=1, sticky=NSEW, padx=20, pady=20)

frame = VerticalScrolledFrame(pairing_frame)
# frame.interior.configure(background='red')
frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
# frame.pack()
pair_frames = []
for i in range(5):
    pair_frames.append(
        LabelFrame(frame.interior, text="Pair #" + str(i + 1), bd=5, relief=RIDGE)
    )
    pair_frames[-1].pack(side=TOP, fill=X, expand=TRUE, padx=20, pady=10)

    pair_frames[-1].grid_columnconfigure(0, weight=1)
    pair_frames[-1].grid_columnconfigure(1, weight=2)
    pair_frames[-1].grid_columnconfigure(1, weight=1)

    pair_frames[-1].grid_rowconfigure(0, weight=1)
    pair_frames[-1].grid_rowconfigure(1, weight=1)
    pair_frames[-1].grid_rowconfigure(2, weight=1)

    Label(
        pair_frames[-1], text=language.translation_json["Content"]["source_dir"] + ":"
    ).grid(row=0, column=0, padx=5, pady=5, sticky=E)
    source_entry = Entry(pair_frames[-1], fg="black", bg="white", justify="left")
    source_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky=EW)
    Tooltip(
        source_entry,
        text=language.translation_json["Tooltip"]["select_source_dir_input"],
    )
    source_entry_button = Button(
        pair_frames[-1],
        text="...",
        command=partial(callback_folder_select, source_entry),
    )
    source_entry_button.grid(row=0, column=2, columnspan=1, padx=0, pady=5, sticky=E)
    Tooltip(
        source_entry_button,
        text=language.translation_json["Tooltip"]["select_source_dir_dialogue"],
    )
    Label(
        pair_frames[-1], text=language.translation_json["Content"]["target_dir"] + ":"
    ).grid(row=1, column=0, padx=5, pady=5, sticky=E)
    target_entry = Entry(pair_frames[-1], fg="black", bg="white", justify="left")
    target_entry.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky=EW)
    Tooltip(
        target_entry,
        text=language.translation_json["Tooltip"]["select_target_dir_input"],
    )
    target_entry_button = Button(
        pair_frames[-1],
        text="...",
        command=partial(callback_folder_select, target_entry),
    )
    target_entry_button.grid(row=1, column=2, columnspan=1, padx=0, pady=5, sticky=E)
    Tooltip(
        target_entry_button,
        text=language.translation_json["Tooltip"]["select_target_dir_dialogue"],
    )

bottom_frame = Frame(window)
bottom_frame.grid(row=2, column=0, columnspan=3, sticky=S, padx=20, pady=20)
Button(
    bottom_frame,
    text=language.translation_json["Content"]["okay"],
    command=partial(
        callback_folder_select,
    ),
).grid(row=0, column=0, columnspan=1, padx=5, pady=0, sticky=E)
Button(
    bottom_frame,
    text=language.translation_json["Content"]["cancel"],
    command=partial(callback_close_window),
).grid(row=0, column=1, columnspan=1, padx=5, pady=0)
Button(
    bottom_frame,
    text=language.translation_json["Content"]["save_settings"],
    command=partial(
        callback_folder_select,
    ),
).grid(row=0, column=2, columnspan=1, padx=5, pady=0, sticky=W)


window.mainloop()
