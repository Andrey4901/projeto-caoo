import tkinter as tk
from controller import Controller
from view import SistemaView

if __name__ == "__main__":
    root = tk.Tk()
    controller = Controller()
    app = SistemaView(root, controller)
    root.mainloop()