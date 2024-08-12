from tkinter import Toplevel, Label, Button, Tk
import tkinter as tk


def wait(message):
    win = Toplevel(root)
    win.transient()
    win.title('Wait')
    Label(win, text=message).pack()
    return win


def wait_a_sec():
    win = wait('Just one second...')
    root.after(1000, win.destroy)


if __name__ == '__main__':
    root = Tk()
    # # button = Button(root, text='do something', command=wait_a_sec)
    # win = wait('Just one second...')
    # root.after(5000, win.destroy)
    # # root.destroy()
    # root.mainloop()

    window = tk.Tk()

    frame_a = tk.Frame()
    label_a = tk.Label(master=frame_a, text="I'm in Frame A")
    label_a.pack()

    frame_b = tk.Frame()
    label_b = tk.Label(master=frame_b, text="I'm in Frame B")
    label_b.pack()

    # Вставка рамок в окне поменялись местами.
    frame_b.pack()
    frame_a.pack()

    window.mainloop()