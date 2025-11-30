import tkinter as tk
from view import SistemaView
from controller import Controller

if __name__ == "__main__":
    try:
        root = tk.Tk()
        controller = Controller()
        app = SistemaView(root, controller)
        root.mainloop()
        
    except KeyboardInterrupt:
        print("Aplicação interrompida pelo usuário.")