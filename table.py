import pandas as pd
from tkinter import Tk, Frame
from tkinter import ttk


# duplicate from data module, need to tie them together
spanish_data_file = './data/Tasks_ItemBank_Spanish.xlsx'
spanish_dataframe = pd.read_excel(spanish_data_file)

# Create the main window
# We need to make this a frame inside our main.py
root = Tk()
root.title("Levante Test")
root.geometry("600x400")

# Create a frame for the Treeview
frame = Frame(root)
frame.pack(fill='both', expand=True)

# Create a Treeview widget
tree = ttk.Treeview(frame, columns=list(spanish_dataframe.columns), show='headings')

# Define headings
for col in spanish_dataframe.columns:
    tree.heading(col, text=col)
    tree.column(col, anchor='center')

# Insert data into the Treeview
for index, row in spanish_dataframe.iterrows():
    tree.insert("", "end", values=list(row))

# Pack the Treeview widget
tree.pack(fill='both', expand=True)

# Run the application
root.mainloop()
