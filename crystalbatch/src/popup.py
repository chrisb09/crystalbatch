from tkinter.messagebox import *
import tkinter as tk


def _create_root():
    root = tk.Tk()
    root.overrideredirect(1)
    root.withdraw()
    return root


def _destroy_root(root):
    root.destroy()


def _helper(function, *args):
    tmp = _create_root()
    function(*args)
    _destroy_root(tmp)


def _callfunction(function, root, *args):
    if root is None:
        _helper(function, *args)
    else:
        function(*args)


def error(title, message, root=None):
    _callfunction(showerror, root, title, message)
    # showerror(title, message)


def warning(title, message, root=None):
    _callfunction(showwarning, root, title, message)
