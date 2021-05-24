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
    res = function(*args)
    _destroy_root(tmp)
    return res


def _callfunction(function, root, *args):
    if root is None:
        return _helper(function, *args)
    else:
        return function(*args)


def error(title, message, root=None):
    return _callfunction(showerror, root, title, message)


def warning(title, message, root=None):
    return _callfunction(showwarning, root, title, message)


def info(title, message, root=None):
    return _callfunction(showinfo, root, title, message)


def yes_no_cancel(title, message, root=None):
    return _callfunction(askyesnocancel, root, title, message)


def yes_no(title, message, root=None):
    return _callfunction(askyesno, root, title, message)


def retry_cancel(title, message, root=None):
    return _callfunction(askretrycancel, root, title, message)


def question(title, message, root=None):
    return _callfunction(askquestion, root, title, message)


def okay_cancel(title, message, root=None):
    return _callfunction(askokcancel, root, title, message)
