from tkinter import Toplevel, Label, Button, Tk


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
    # button = Button(root, text='do something', command=wait_a_sec)
    win = wait('Just one second...')
    root.after(5000, win.destroy)
    # root.destroy()
    root.mainloop()
