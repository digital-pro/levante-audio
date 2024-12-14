import os
import customtkinter as ctk
from tkinter import ttk, filedialog, StringVar
from dotenv import load_dotenv
from PIL import Image
from utils.gui_functions import *
from threading import Thread
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
import time
import re
import logging
import sys

# in case we need an add-in table
from ttkwidgets import Table

# Needed if we put our import code in main.py
import pandas as pd
# Or try and use our data loaders
#import levanteData


# Modes: "System" (standard), "Dark", "Light"
ctk.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
ctk.set_default_color_theme("dark-blue")


load_dotenv()
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class LevanteAudio:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Levante Audio Test")
        self.window_width = 1280
        self.window_height = 600
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        # Calculate the x and y coordinates to center the window
        self.x = (self.screen_width / 2) - (self.window_width / 2)
        self.y = (self.screen_height / 2) - (self.window_height / 2)

        # Set the window position and size
        self.root.geometry('%dx%d+%d+%d' % (self.window_width,
                           self.window_height, self.x, self.y))

        # self.root.geometry("1400x800")
        self.image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "images")
        self.voices_data = fetch_voices(ELEVENLABS_API_KEY)
        self.chat_image = ctk.CTkImage(light_image=Image.open(os.path.join(self.image_path, "chat_dark.png")),
                                       dark_image=Image.open(os.path.join(self.image_path, "chat_light.png")), size=(20, 20))
        self.play_image = ctk.CTkImage(light_image=Image.open(
            os.path.join(self.image_path, "play.png")), size=(80, 80))
        self.pause_image = ctk.CTkImage(light_image=Image.open(
            os.path.join(self.image_path, "pause.png")), size=(80, 80))

        self.current_selected_row = None
        self.history_frame_visible = False
        self.configure_grid()
        # self.init_ui()
        self.audio_data_played = 0
        self.temp_audio_file_name = None
        self.audio_playback_finished = False
        self.is_playing = False
        self.is_paused = False
        self.is_recording = False
        self.stream = None
        # Need both of these values to correctly update the audio position in the GUI
        self.audio_length = 0
        self.correct_audio_pos = 0
        # Used by our tkinter gui element named "actual_song_lbl"   > Shows the name of the current song being played.
        self.current_audio = StringVar(value="")
        self.status = StringVar()
        # Used by our tkinter gui element named "status_label"      > Playing | Paused | Stopped
        self.status.set("Stopped")
        self.new_audio_position = 0
        self.current_length = 0

        self.root.mainloop()

    def configure_grid(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(6, weight=1)

    def create_top_frame(self):
        top_frame = ctk.CTkFrame(self.root, height=80, fg_color="transparent")
        top_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=0)
        return top_frame

    # This is where we want our tables to go
    def create_spanish_table(self):

        spanish_data_file = './data/Tasks_ItemBank_Spanish.xlsx'
        spanish_dataframe = pd.read_excel(spanish_data_file)

        # Create a table widget in our frame
        columns = ["ID", "task", "english", "spanish"]
        spanish_table = Table(self.root, columns=columns, height=6)
        spanish_table.grid(row=2, column=1, sticky="nsew", padx=15, pady=0)
        
        for col in columns:
            spanish_table.heading(col, text=col)
            spanish_table.column(col, width=100, stretch=False)
            # Define headings
            style = ttk.Style(self.root)
            style.theme_use('alt')
            
        for i in range(12): # 12 for debugging
            spanish_table.insert('', 'end', iid=i,
                 values=(i, i) + tuple(i + 10 * j for j in range(2, 7)))

        return spanish_table

# for after we get the spanish table working    
#    def create_german_table(self):
#        return german_table
    
    def create_text_box(self):
        text_box = ctk.CTkTextbox(self.root, wrap=ctk.WORD)
        text_box.grid(row=2, column=1, sticky="nsew", padx=10, pady=(10, 0))
        text_box.bind('<Control-v>', lambda event: custom_paste(event,
                      text_box, self.char_count, self.generate_button))
        text_box.bind('<Any-KeyPress>', lambda event: check_character_limit(event,
                      text_box, self.char_count, self.generate_button))
        text_box.bind('<Button-1>', lambda event: check_character_limit(
            event, text_box, self.char_count, self.generate_button))
        return text_box

    def create_text_status_frame(self):
        self.text_status_frame = ctk.CTkFrame(
            self.root, fg_color="transparent")
        self.text_status_frame.grid(row=3, column=1, sticky="new")

        char_count = ctk.CTkLabel(
            self.text_status_frame, text="0/5000", font=("Arial", 12), state="disabled")
        char_count.pack(side=ctk.LEFT, padx=10, pady=0)

        right_button = ctk.CTkLabel(
            self.text_status_frame, text="total quota used: 0 ", font=("Arial", 12), state="disabled")
        right_button.pack(side=ctk.RIGHT, padx=10, pady=0)

        return char_count, right_button

    def create_sample_frame(self):
        self.sample_frame = ctk.CTkFrame(self.root)
        self.sample_frame.grid(row=0, column=1, sticky="new", padx=10)

        settings_label = ctk.CTkLabel(
            self.sample_frame, text="Settings", font=("Arial", 12), state="disabled")
        settings_label.pack(side=ctk.LEFT, padx=10, pady=(5, 0))

        preview_label = ctk.CTkLabel(
            self.sample_frame, text="Preview ", font=("Arial", 12), state="disabled")
        preview_label.pack(side=ctk.RIGHT, padx=10, pady=(5, 0))

        return settings_label, preview_label

    def create_generate_button_frame(self):
        generate_button_frame = ctk.CTkFrame(
            self.root, fg_color="transparent")
        generate_button_frame.grid(row=5, column=1, sticky="ew", pady=10)
        self.progressbar = ctk.CTkProgressBar(generate_button_frame)
        self.progressbar.configure(mode="indeterminate")
        self.generate_button = ctk.CTkButton(generate_button_frame, text="Generate", command=lambda: Thread(target=generate_async, args=(self, ELEVENLABS_API_KEY, self.right_button, self.progressbar, self.generate_button)).start()
                                             )
        self.generate_button.pack(padx=10, pady=10, fill="x")

        return generate_button_frame

    def create_voice_selection_frame(self, top_frame):
        voice_selection_frame = ctk.CTkFrame(
            top_frame, fg_color="transparent")
        voice_selection_frame.pack(
            side="left", padx=0, pady=(0, 0), fill="both", expand=True)
        voice_selection_frame.update_idletasks()

        self.preview_button = ctk.CTkButton(voice_selection_frame, corner_radius=8, width=4, border_spacing=10,
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            image=self.chat_image, anchor="e", text="", command=lambda: play_voice_preview(self.voices_data, self.voice_selection_optionmenu, grab_preview))
        self.preview_button.pack(side="right")
        voices = fetch_voices(ELEVENLABS_API_KEY)
        voice_names = ["Select voice:"] + [voice['name'] for voice in voices]
        self.voice_selection_optionmenu = ctk.CTkOptionMenu(
            voice_selection_frame, values=voice_names,
            command=self.on_voice_selection_changed, dynamic_resizing=True)
        self.voice_selection_optionmenu.pack(
            side="left", pady=5, fill="x")

    def on_voice_selection_changed(self, *args):
        if self.history_frame_visible:
            self.populate_table()

    def create_slider_bar_frame(self):
        self.slider_bar_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.slider_bar_frame.grid(row=4, column=1, padx=(
            20, 0), pady=(20, 0), sticky="nsew")

        self.create_stability_slider_frame(self.slider_bar_frame)
        self.create_clarity_slider_frame(self.slider_bar_frame)

    def create_stability_slider_frame(self, slider_bar_frame):
        stability_slider_frame = ctk.CTkFrame(
            slider_bar_frame, fg_color="transparent")
        stability_slider_frame.pack(fill="x")

        stability_label = ctk.CTkLabel(
            stability_slider_frame, text="Stability", anchor="w")
        stability_label.pack(side="top", padx=10, pady=(5, 5), anchor="w")

        slider_1 = ctk.CTkSlider(stability_slider_frame, from_=0, to=1,
                                 number_of_steps=100, command=self.update_stability_value)
        slider_1.pack(side="left", padx=(10, 10),
                      pady=(5, 10), fill="x", expand=True)

        self.stability_val = ctk.CTkLabel(stability_slider_frame, text="")
        self.stability_val.pack(side="left", padx=(0, 20), pady=(10, 10))

        default_slider_value = 0.75
        slider_1.set(default_slider_value)
        self.update_stability_value(default_slider_value)

    def create_clarity_slider_frame(self, slider_bar_frame):
        clarity_slider_frame = ctk.CTkFrame(
            slider_bar_frame, fg_color="transparent")
        clarity_slider_frame.pack(fill="x")

        clarity_label = ctk.CTkLabel(
            clarity_slider_frame, text="Clarity + Similarity Enhancement", anchor="w")
        clarity_label.pack(side="top", padx=10, pady=(5, 5), anchor="w")

        slider_2 = ctk.CTkSlider(clarity_slider_frame, from_=0, to=1,
                                 number_of_steps=100, command=self.update_clarity_value)
        slider_2.pack(side="left", padx=(10, 10),
                      pady=(5, 10), fill="x", expand=True)

        self.clarity_val = ctk.CTkLabel(clarity_slider_frame, text="")
        self.clarity_val.pack(side="left", padx=(0, 20), pady=(10, 10))

        default_slider_value = 0.75
        slider_2.set(default_slider_value)
        self.update_clarity_value(default_slider_value)

    def play_button_check(self):
        if self.is_playing:  # If a song is playing
            # Changes the button from "Play" to "Pause"
            self.play_button.configure(image=self.pause_image)

            self.root.update()
        elif self.is_paused:  # If a song is paused
            # Changes the button from "Pause" to "Resume"
            self.play_button.configure(image=self.play_image)

            self.root.update()
        elif self.is_stopped:  # If a song is stopped
            # Changes the button to "Play"
            self.play_button.configure(image=self.play_image)
            self.root.update()

    # Function that sets the main booleans to True or False depending on the input parameter.
    def boolean_switch(self, input):
        if input == "play":
            self.is_paused = False
            self.is_stopped = False
            self.is_playing = True
        elif input == "pause":
            self.is_playing = False
            self.is_stopped = False
            self.is_paused = True
        elif input == "stop":
            self.is_playing = False
            self.is_paused = False
            self.is_stopped = True
        else:
            print("[DEBUG] Error in boolean_switch function: Invalid input.")

    # --------------------------------------------------------------------------------------------

    def update_table_style(self):
        appearance_mode = ctk.get_appearance_mode()

        if appearance_mode == "System":
            system_theme = ctk.get_system_theme()
            if system_theme == "Light":
                x = 0
            elif system_theme == "Dark":
                x = 1
            else:
                # Default to Light if the system theme is not recognized
                x = 0
        elif appearance_mode == "Light":
            x = 0
        elif appearance_mode == "Dark":
            x = 1

        background_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][x]
        text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"][x]

        self.style.configure("Treeview",
                             background=background_color,
                             foreground=text_color,
                             rowheight=120,
                             fieldbackground=background_color,
                             bordercolor="#343638",
                             borderwidth=10)
        self.table.update_idletasks()

    def on_treeview_select(self, event, root):
        # Check if there is a selected item
        if not self.table.selection():
            return
        selected_item = self.table.selection()[0]
        history_item_id = self.table.item(selected_item, "tags")[0]
        delay = 50

        # Stop and unload the current audio
        stop_and_unload_audio(self)

        # Close the current stream if it's playing
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Load the new audio after a short delay
        self.root.after(delay, lambda: get_history_audio(
            self, history_item_id))

    def populate_table(self):
        print("Populating table...")

        # Clear the current content of the table
        for item in self.table.get_children():
            self.table.delete(item)

        selected_voice_name = self.voice_selection_optionmenu.get()
        data = fetch_history(ELEVENLABS_API_KEY)
        max_line_width = 75

        for item in data:
            # Skip the item if the voice name doesn't match the selected voice
            if selected_voice_name != "Select voice:" and item["voice_name"] != selected_voice_name:
                continue

            wrapped_text = wrap_text(item["text"], max_line_width)
            formatted_date = unix_to_date(item["date_unix"])
            settings = item["settings"]
            stability = settings.get("stability", "N/A")
            similarity_boost = settings.get("similarity_boost", "N/A")
            self.table.insert("", "end", tags=(str(item["history_item_id"]),), values=(
                f"{item['voice_name']}\n{formatted_date}", f"Stability: {stability}\nSimilarity Boost: {similarity_boost}", wrapped_text))
        print("Populated table successfully.")


    # --------------------------------------------------------------------------------------------

    def create_main_content(self):
        self.top_frame = self.create_top_frame()
        self.text_box = self.create_text_box()
        #self.spanish_table = self.create_spanish_table()
        self.char_count, self.right_button = self.create_text_status_frame()
        self.settings_label, self.preview_label = self.create_sample_frame()
        self.generate_button_frame = self.create_generate_button_frame()
        self.create_voice_selection_frame(self.top_frame)
        self.create_slider_bar_frame()

        update_quota(ELEVENLABS_API_KEY, self.right_button)

    def update_stability_value(self, val):
        percentage = float(val) * 100
        self.stability_val.configure(text=f"{percentage:.0f}%")

    def update_clarity_value(self, val):
        percentage = float(val) * 100
        self.clarity_val.configure(text=f"{percentage:.0f}%")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if self.history_frame_visible:
            # Delay the call to update_table_style
            self.root.after(30, self.update_table_style)
        # Delay the call to update_idletasks
        self.root.after(30, self.root.update_idletasks)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self, button_id):
        if button_id == 1:
            self.switch_to_synthesize_speech()
        elif button_id == 2:
            print("Voice editing functionality coming soon!")
        elif button_id == 3:
            self.create_history_frame()

    def trigger_dummy_event(self):
        dummy_event = type("DummyEvent", (object,), {"widget": self.table})()
        self.on_treeview_select(dummy_event, self.root)

    def switch_to_synthesize_speech(self):
        print("Switching to Synthesize speech view")
        self.clear_content_frames()
        self.history_frame_visible = False
        self.sample_frame.grid(row=0, column=1, sticky="new", padx=10)
        self.top_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=0)
        #self.spanish_table.grid(row=2, column=1, sticky="nsew", padx=15, pady=0)
        self.text_box.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        self.text_status_frame.grid(row=4, column=1, sticky="new")
        self.slider_bar_frame.grid(row=5, column=1, padx=(
            20, 0), pady=(20, 0), sticky="nsew")
        self.generate_button_frame.grid(row=6, column=1, sticky="ew", pady=10)

    def create_history_frame(self):
        self.clear_content_frames()
        ctk.AppearanceModeTracker.add(self.update_table_style)
        self.history_frame_visible = True
        self.sample_frame.grid(row=0, column=1, sticky="new", padx=10)
        self.top_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=0)
        #self.spanish_table.grid(row=2, column=1, sticky="nsew", padx=15, pady=0)
        self.history_frame = ctk.CTkFrame(self.root)
        self.history_frame.grid(
            row=3, column=1, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.add_menu_display = ctk.CTkFrame(self.history_frame,
                                             corner_radius=15)
        self.add_menu_display.grid(pady=15, padx=15, sticky="nwse")
        self.history_frame.grid_rowconfigure(0, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.add_menu_display.grid_rowconfigure(0, weight=1)
        self.add_menu_display.grid_columnconfigure(0, weight=1)
        self.create_table()
        self.update_table_style()
        self.populate_table()

    def clear_content_frames(self):
        for widget in self.root.grid_slaves():
            if widget.grid_info()["column"] == 1 and widget.grid_info()["row"] > 1 and widget.grid_info()["row"] != 6:
                widget.grid_forget()


if __name__ == "__main__":
    LevanteAudio()
