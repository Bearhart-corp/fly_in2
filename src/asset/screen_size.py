import tkinter as tk


def screen_size() -> tuple:
    root = tk.Tk()
    largeur = root.winfo_screenwidth()
    hauteur = root.winfo_screenheight()
    root.destroy()
    return (largeur, hauteur)
