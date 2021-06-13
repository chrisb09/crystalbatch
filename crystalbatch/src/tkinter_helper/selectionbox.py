import tkinter as tk
from tkinter import *
from tkinter import ttk


class Selectionbox(ttk.Combobox):

    values = None #Displayed
    return_values = None #return value respectively

    def __init__(self, parent, **kvargs):
        super().__init__(parent, **kvargs)
