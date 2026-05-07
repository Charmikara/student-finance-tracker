import tkinter as tk

from ui.app import StudentFinanceGUI


if __name__ == "__main__":
    root_window = tk.Tk()
    app = StudentFinanceGUI(root_window)
    root_window.mainloop()
