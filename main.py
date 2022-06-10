"""Run the app here."""
import tkinter as tk
from download_data import DownloadData

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
W_WIDTH = 250
W_HEIGHT = 100
center_x = int(screen_width / 2 - W_WIDTH / 2)
center_y = int(screen_height / 2 - W_HEIGHT / 2)
# place the window at the center
root.geometry(f'{W_WIDTH}x{W_HEIGHT}+{center_x}+{center_y}')
download_frame = DownloadData(root)
download_frame.grid(row=0, column=0, sticky=tk.NSEW)
root.mainloop()
