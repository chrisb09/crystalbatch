import tkinter as tk


class StringVariable(tk.StringVar):

    callback = None

    def __init__(self, callback=None, master=None, value=None, name=None):
        print()
        super().__init__(master=master, value=value, name=name)
        self.callback = callback

    def get(self):
        return super().get()

    def set(self, value):
        if self.callback is not None:
            res = self.callback(self, value)
        res = None
        if res is None:
            res = value
        return super().set(res)
