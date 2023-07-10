import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
from speech.speech import SpeechRecognition
import threading
import json
import requests
import time
import os, sys
import queue
from pynput.keyboard import Key, Controller
import vgamepad as vg
from vosk import Model, KaldiRecognizer, SetLogLevel

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class WizardVoiceGUI:
    def __init__(self, master):
        self.master = master
        master.title("Wizard's Voice")
        master.option_add("*tearOff", False)
        self.casting = SpeechRecognition(master)
        self.logged_in = False

        self.data_path = os.getenv('LOCALAPPDATA')
        self.data_path += "\\WizardsVoice"

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        master.columnconfigure(index=0, weight=1)
        master.columnconfigure(index=1, weight=1)
        master.rowconfigure(index=1, weight=1)
        master.rowconfigure(index=2, weight=1)

        self.style = ttk.Style(master)
        master.tk.call("source", resource_path("forest-dark.tcl"))
        self.style.theme_use("forest-dark")

        # Create a Frame for the Spellconfiguration
        self.spells_frame = ttk.LabelFrame(master, text="Set spells according to your ingame layout", padding=(10, 0))
        self.spells_frame.grid(row=0, column=0, padx=(20, 10), sticky="nsew")

        self.f1_frame = ttk.LabelFrame(self.spells_frame, text="F1", padding=(10, 10))
        self.f1_frame.grid(row=0, column=0, padx=(20, 10), sticky="nsew")
        self.f2_frame = ttk.LabelFrame(self.spells_frame, text="F2", padding=(10, 10))
        self.f2_frame.grid(row=1, column=0, padx=(20, 10), sticky="nsew")
        self.f3_frame = ttk.LabelFrame(self.spells_frame, text="F3", padding=(10, 10))
        self.f3_frame.grid(row=2, column=0, padx=(20, 10), sticky="nsew")
        self.f4_frame = ttk.LabelFrame(self.spells_frame, text="F4", padding=(10, 10))
        self.f4_frame.grid(row=3, column=0, padx=(20, 10), sticky="nsew")
        self.additional_frame = ttk.LabelFrame(self.spells_frame, text="Additional Commands")
        self.additional_frame.grid(row=4, column=0, padx=(20, 10), pady=(10, 5), sticky="nsew")

        # Key press options - Keyboard
        self.key_options = {
            "1": {
                "card": "f1",
                "slot": "1"
            },
            "2": {
                "card": "f1",
                "slot": "2"
            },
            "3": {
                "card": "f1",
                "slot": "3"
            },
            "4": {
                "card": "f1",
                "slot": "4"
            },
            "5": {
                "card": "f2",
                "slot": "1"
            },
            "6": {
                "card": "f2",
                "slot": "2"
            },
            "7": {
                "card": "f2",
                "slot": "3"
            },
            "8": {
                "card": "f2",
                "slot": "4"
            },
            "9": {
                "card": "f3",
                "slot": "1"
            },
            "10": {
                "card": "f3",
                "slot": "2"
            },
            "11": {
                "card": "f3",
                "slot": "3"
            },
            "12": {
                "card": "f3",
                "slot": "4"
            },
            "13": {
                "card": "f4",
                "slot": "1"
            },
            "14": {
                "card": "f4",
                "slot": "2"
            },
            "15": {
                "card": "f4",
                "slot": "3"
            },
            "16": {
                "card": "f4",
                "slot": "4"
            }
        }
        
        self.all_castable_spells = ["DISABLED", "ACCIO", "ARRESTO MOMENTUM", "AVADA KEDAVRA", "BOMBARDA", "BUILD", "CATCH", "CHANGE", "CONFRINGO", "CONFUNDO", "CRUCIO", "DEPULSO", "DESCENDO", "DIFFINDO", "EVANESCO", "EXPELLIARMUS", "FEED", 
                                    "FLIPENDO", "GLACIUS", "IMPERIO", "INCENDIO", "INVISIBLE", "LEVIOSO", "LUMOS", "MAXIMA", "OBLIVIATE", "OPPUGNO", "REPARO", "PESTIS", "PET", "STUPEFY", "TRANSFORM", "WINGARDIUM LEVIOSA"]
        
        self.ancient_options = ["DISABLED", "ANCIENT", "POWER"]
        self.ancient_throw_options = ["DISABLED", "THROW", "SMASH", "BARREL"]
        self.broom_options = ["DISABLED", "BROOM", "FLY", "NIMBUS", "FIREBOLT", "THUNDERBOLT"]
        self.fly_mount_options = ["DISABLED", "HIPPOGRIFF", "THESTRAL", "DRAGON", "HIGHWING", "CALIGO", "SEPULCHRIA"]
        self.walk_mount_options = ["DISABLED", "GRAPHORN", "BULLDOZER"]
        self.tool_options = ["DISABLED", "TOOL", "CABBAGE", "MANDRAKE", "TENTACULA", "POTION"]
        self.additional_options = ["ACTIVE", "DISABLED"]

        # Spellconfiguration
        self.spell_menu_f1_1 = ttk.Combobox(self.f1_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f1_1.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f1_1.grid(row=0, column=0, padx=5, sticky="nsew")
        self.spell_menu_f1_2 = ttk.Combobox(self.f1_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f1_2.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f1_2.grid(row=0, column=1, padx=5, sticky="nsew")
        self.spell_menu_f1_3 = ttk.Combobox(self.f1_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f1_3.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f1_3.grid(row=0, column=2, padx=5, sticky="nsew")
        self.spell_menu_f1_4 = ttk.Combobox(self.f1_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f1_4.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f1_4.grid(row=0, column=3, padx=5, sticky="nsew")
        self.spell_menu_f2_1 = ttk.Combobox(self.f2_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f2_1.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f2_1.grid(row=0, column=0, padx=5, sticky="nsew")
        self.spell_menu_f2_2 = ttk.Combobox(self.f2_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f2_2.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f2_2.grid(row=0, column=1, padx=5, sticky="nsew")
        self.spell_menu_f2_3 = ttk.Combobox(self.f2_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f2_3.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f2_3.grid(row=0, column=2, padx=5, sticky="nsew")
        self.spell_menu_f2_4 = ttk.Combobox(self.f2_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f2_4.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f2_4.grid(row=0, column=3, padx=5, sticky="nsew")
        self.spell_menu_f3_1 = ttk.Combobox(self.f3_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f3_1.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f3_1.grid(row=0, column=0, padx=5, sticky="nsew")
        self.spell_menu_f3_2 = ttk.Combobox(self.f3_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f3_2.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f3_2.grid(row=0, column=1, padx=5, sticky="nsew")
        self.spell_menu_f3_3 = ttk.Combobox(self.f3_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f3_3.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f3_3.grid(row=0, column=2, padx=5, sticky="nsew")
        self.spell_menu_f3_4 = ttk.Combobox(self.f3_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f3_4.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f3_4.grid(row=0, column=3, padx=5, sticky="nsew")
        self.spell_menu_f4_1 = ttk.Combobox(self.f4_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f4_1.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f4_1.grid(row=0, column=0, padx=5, sticky="nsew")
        self.spell_menu_f4_2 = ttk.Combobox(self.f4_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f4_2.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f4_2.grid(row=0, column=1, padx=5, sticky="nsew")
        self.spell_menu_f4_3 = ttk.Combobox(self.f4_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f4_3.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f4_3.grid(row=0, column=2, padx=5, sticky="nsew")
        self.spell_menu_f4_4 = ttk.Combobox(self.f4_frame, state="readonly", values=self.all_castable_spells)
        self.spell_menu_f4_4.bind('<<ComboboxSelected>>', self.save_preferences)
        self.spell_menu_f4_4.grid(row=0, column=3, padx=5, sticky="nsew")

        self.revelio_frame = ttk.LabelFrame(self.additional_frame, text="Command: Revelio")
        self.revelio_frame.grid(row=0, column=0, padx=(5, 5),  sticky="nsew")
        self.revelio = ttk.Combobox(self.revelio_frame, state="readonly", values=self.additional_options)
        self.revelio.bind('<<ComboboxSelected>>', self.save_preferences)
        self.revelio.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.protego_frame = ttk.LabelFrame(self.additional_frame, text="Command: Protego")
        self.protego_frame.grid(row=0, column=1, padx=(5, 5),  sticky="nsew")
        self.protego = ttk.Combobox(self.protego_frame, state="readonly", values=self.additional_options)
        self.protego.bind('<<ComboboxSelected>>', self.save_preferences)
        self.protego.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
        
        self.inventory_frame = ttk.LabelFrame(self.additional_frame, text="Command: Inventory")
        self.inventory_frame.grid(row=0, column=2, padx=(5, 5), sticky="nsew")
        self.inventory = ttk.Combobox(self.inventory_frame, state="readonly", values=self.additional_options)
        self.inventory.bind('<<ComboboxSelected>>', self.save_preferences)
        self.inventory.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
                
        self.gear_frame = ttk.LabelFrame(self.additional_frame, text="Command: Gear")
        self.gear_frame.grid(row=0, column=3, padx=(5, 5), sticky="nsew")
        self.gear = ttk.Combobox(self.gear_frame, state="readonly", values=self.additional_options)
        self.gear.bind('<<ComboboxSelected>>', self.save_preferences)
        self.gear.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.map_frame = ttk.LabelFrame(self.additional_frame, text="Command: Map")
        self.map_frame.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.map = ttk.Combobox(self.map_frame, state="readonly", values=self.additional_options)
        self.map.bind('<<ComboboxSelected>>', self.save_preferences)
        self.map.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.quests_frame = ttk.LabelFrame(self.additional_frame, text="Command: Quests")
        self.quests_frame.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.quests = ttk.Combobox(self.quests_frame, state="readonly", values=self.additional_options)
        self.quests.bind('<<ComboboxSelected>>', self.save_preferences)
        self.quests.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
        
        self.challenges_frame = ttk.LabelFrame(self.additional_frame, text="Command: Challenges")
        self.challenges_frame.grid(row=1, column=2, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.challenges = ttk.Combobox(self.challenges_frame, state="readonly", values=self.additional_options)
        self.challenges.bind('<<ComboboxSelected>>', self.save_preferences)
        self.challenges.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
                
        self.talents_frame = ttk.LabelFrame(self.additional_frame, text="Command: Talents")
        self.talents_frame.grid(row=1, column=3, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.talents = ttk.Combobox(self.talents_frame, state="readonly", values=self.additional_options)
        self.talents.bind('<<ComboboxSelected>>', self.save_preferences)
        self.talents.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.heal_frame = ttk.LabelFrame(self.additional_frame, text="Command: Heal")
        self.heal_frame.grid(row=2, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.heal = ttk.Combobox(self.heal_frame, state="readonly", values=self.additional_options)
        self.heal.bind('<<ComboboxSelected>>', self.save_preferences)
        self.heal.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.alohomora_frame = ttk.LabelFrame(self.additional_frame, text="Command: Alohomora")
        self.alohomora_frame.grid(row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.alohomora = ttk.Combobox(self.alohomora_frame, state="readonly", values=self.additional_options)
        self.alohomora.bind('<<ComboboxSelected>>', self.save_preferences)
        self.alohomora.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.petrificus_frame = ttk.LabelFrame(self.additional_frame, text="Command: Petrificus Totalus")
        self.petrificus_frame.grid(row=2, column=2, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.petrificus = ttk.Combobox(self.petrificus_frame, state="readonly", values=self.additional_options)
        self.petrificus.bind('<<ComboboxSelected>>', self.save_preferences)
        self.petrificus.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")



        self.additional_3_frame = ttk.LabelFrame(self.additional_frame, text="Ancient Magic")
        self.additional_3_frame.grid(row=3, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.ancient = ttk.Combobox(self.additional_3_frame, state="readonly", values=self.ancient_options)
        self.ancient.bind('<<ComboboxSelected>>', self.save_preferences)
        self.ancient.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.additional_4_frame = ttk.LabelFrame(self.additional_frame, text="Ancient Throw")
        self.additional_4_frame.grid(row=3, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.ancient_throw = ttk.Combobox(self.additional_4_frame, state="readonly", values=self.ancient_throw_options)
        self.ancient_throw.bind('<<ComboboxSelected>>', self.save_preferences)
        self.ancient_throw.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.additional_5_frame = ttk.LabelFrame(self.additional_frame, text="Broom")
        self.additional_5_frame.grid(row=3, column=2, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.broom = ttk.Combobox(self.additional_5_frame, state="readonly", values=self.broom_options)
        self.broom.bind('<<ComboboxSelected>>', self.save_preferences)
        self.broom.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.additional_6_frame = ttk.LabelFrame(self.additional_frame, text="Mount 1")
        self.additional_6_frame.grid(row=3, column=3, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.mount_1 = ttk.Combobox(self.additional_6_frame, state="readonly", values=self.walk_mount_options)
        self.mount_1.bind('<<ComboboxSelected>>', self.save_preferences)
        self.mount_1.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.additional_7_frame = ttk.LabelFrame(self.additional_frame, text="Mount 2")
        self.additional_7_frame.grid(row=4, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.mount_2 = ttk.Combobox(self.additional_7_frame, state="readonly", values=self.fly_mount_options)
        self.mount_2.bind('<<ComboboxSelected>>', self.save_preferences)
        self.mount_2.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")

        self.additional_8_frame = ttk.LabelFrame(self.additional_frame, text="Tool")
        self.additional_8_frame.grid(row=4, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.tool = ttk.Combobox(self.additional_8_frame, state="readonly", values=self.tool_options)
        self.tool.bind('<<ComboboxSelected>>', self.save_preferences)
        self.tool.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
    
        # Create a Frame for input widgets
        self.widgets_frame = ttk.Frame(master, padding=(0, 0, 0, 10))
        self.widgets_frame.grid(row=0, column=1, padx=10, pady=(20, 0), sticky="nsew")
        self.widgets_frame.columnconfigure(index=0, weight=1)

        self.input_configure_frame = ttk.LabelFrame(self.widgets_frame, text="Configure Input Devices")
        self.input_configure_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        self.input_configure_frame.columnconfigure(index=0, weight=1)

        self.microphone_frame = ttk.LabelFrame(self.input_configure_frame, text="Microphone")
        self.microphone_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        self.microphone_frame.columnconfigure(index=0, weight=1)

        # Configure Input Device
        self.devices = sd.query_devices()
        self.device_names = []
        for device in self.devices:
            self.device_names.append(device["name"])
        self.device_names.insert(0, "No mic detected")
        self.input_device = ttk.Combobox(self.microphone_frame, state="readonly", values=self.device_names)
        try:
            self.input_device.current(sd.default.device[0]+1)
        except:
            self.input_device.current(0)
        self.input_device.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.playing_device_frame = ttk.LabelFrame(self.input_configure_frame, text="Input Device")
        self.playing_device_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.playing_device_frame.columnconfigure(index=0, weight=1)

        self.playing_device = ttk.Combobox(self.playing_device_frame, state="readonly", values=["Controller", "Keyboard"])
        self.playing_device.bind('<<ComboboxSelected>>', self.save_preferences)
        self.playing_device.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")

        self.get_preferences()
        self.update_spell_order()

        # Accentbutton
        self.start_button = ttk.Button(self.widgets_frame, text="Start Listening", style="Accent.TButton", command=self.start_recognizer_thread)
        self.start_button.grid(row=4, column=0, padx=5, pady=(25, 0), sticky="nsew")

        # Button
        self.stop_button = ttk.Button(self.widgets_frame, text="Stop Listening", command=self.stop_recognizer_thread)
        self.stop_button.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

        self.status_label = ttk.Label(self.widgets_frame, text="Don't forget to match the spells to your ingame setup!", font=28)
        self.status_label.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")

        self.progress_frame = ttk.LabelFrame(self.widgets_frame, text="Last casted spell:")
        self.progress_frame.grid(row=7, column=0, padx=5, pady=(27, 0), sticky="nsew")

        self.progress_label = ttk.Label(self.progress_frame, text="{}".format(self.casting.progress_message))
        self.progress_label.grid(row=0, column=0, padx=5, pady=(15, 0), sticky="nsew")

        self.error_frame = ttk.LabelFrame(self.widgets_frame, text="Errors:")
        self.error_frame.grid(row=8, column=0, padx=5, pady=(27, 0), sticky="nsew")

        self.error_label = ttk.Label(self.error_frame, text="{}".format(self.casting.error_message))
        self.error_label.grid(row=0, column=0, padx=5, pady=(15, 0), sticky="nsew")

        # Sizegrip
        self.sizegrip = ttk.Sizegrip(master)
        self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

        # Center the window, and set minsize
        self.master.update()
        self.master.minsize(root.winfo_width(), root.winfo_height())

        self.running = False

        self.valid_license = False
        self.license_key = self.get_license_key()
        if self.license_key == "no_license":
            self.open_license_window(master)
        else:
            self.check_valid_license_key(self.license_key)

    def open_license_window(self, master):
        # Create a new window
        self.license_window = tk.Toplevel(master)
        self.license_window.title("License Verification")
        # Set the size and position of the login window
        self.license_window.geometry("490x135")
        main_width = root.winfo_width()
        main_height = root.winfo_height()
        x = root.winfo_x() + (main_width // 2) - (300 // 2)
        y = root.winfo_y() + (main_height // 2) - (200 // 2)
        self.license_window.geometry("+{}+{}".format(x, y))

        # Disable the main window while the login window is open
        self.license_window.grab_set()

        # Add widgets to the window
        username_label = ttk.Label(self.license_window, text="Enter a valid license key:")
        username_entry = ttk.Entry(self.license_window, width=40)
        get_key_label = ttk.Label(self.license_window, text="Get your license key here: https://hawktopos.gumroad.com/l/WizardsVoice")
        confirm_key_button = ttk.Button(self.license_window, text="Confirm", style="Accent.TButton", command= lambda:self.check_initial_license_key(username_entry.get()))
        
        # Layout the widgets in the window
        username_label.grid(row=0, column=0, padx=10, pady=10)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        get_key_label.grid(row=3, columnspan=2, padx=10, pady=10)
        confirm_key_button.grid(row=2, column=1)
        
        # Run the window
        self.license_window.mainloop()

    def check_valid_license_key(self, license_key_input):
        # Add your code to verify the login credentials here
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = 'product_id=1FEwbiDgBJdNdVYZfb2pzA==&increment_uses_count=false&license_key={}'.format(license_key_input)

        response = requests.post('https://api.gumroad.com/v2/licenses/verify', headers=headers, data=data)
        json_response = response.json()
        if json_response["success"] == True and json_response["uses"] == 1 and json_response["purchase"]["refunded"] == False:
            self.valid_license = True
        else:
            self.valid_license = False
            self.open_license_window(self.master)

    def check_initial_license_key(self, license_key_input):
        # Add your code to verify the login credentials here
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = 'product_id=1FEwbiDgBJdNdVYZfb2pzA==&license_key={}'.format(license_key_input)

        response = requests.post('https://api.gumroad.com/v2/licenses/verify', headers=headers, data=data)
        json_response = response.json()
        if json_response["success"] == True and json_response["uses"] == 1 and json_response["purchase"]["refunded"] == False:
            messagebox.showinfo(title="Success", message="Key validation: SUCCESS!")
            with open(resource_path("{}\\license_key.txt".format(self.data_path)), "w+") as f:
                f.write(license_key_input)
            self.valid_license = True
            self.license_window.destroy()
        else: 
            messagebox.showerror(title="Invalid Key", message="Invalid license key. Please enter a valid key!")

    def get_license_key(self):
        try:
            with open(resource_path("{}\\license_key.txt".format(self.data_path)), "r") as f:
                return f.readline()
        except:
            return "no_license"

    def update_spell_order(self):
        self.spell_order = []
        for item in self.user_preferences["spells"].items():
            self.spell_order.append(self.all_castable_spells[item[1]])
        self.spell_dict = {}
        for i in range(len(self.spell_order)):
            if self.spell_order[i] not in self.spell_dict:
                self.spell_dict[self.spell_order[i]] = self.key_options["{}".format(i+1)]
        self.casting.spell_keys = self.spell_dict
        

    def save_preferences(self, pos):
        # Save the user preferences
        self.user_preferences = {
            "spells": {
                "spell_menu_f1_1": self.spell_menu_f1_1.current(),
                "spell_menu_f1_2": self.spell_menu_f1_2.current(),
                "spell_menu_f1_3": self.spell_menu_f1_3.current(),
                "spell_menu_f1_4": self.spell_menu_f1_4.current(),
                "spell_menu_f2_1": self.spell_menu_f2_1.current(),
                "spell_menu_f2_2": self.spell_menu_f2_2.current(),
                "spell_menu_f2_3": self.spell_menu_f2_3.current(),
                "spell_menu_f2_4": self.spell_menu_f2_4.current(),
                "spell_menu_f3_1": self.spell_menu_f3_1.current(),
                "spell_menu_f3_2": self.spell_menu_f3_2.current(),
                "spell_menu_f3_3": self.spell_menu_f3_3.current(),
                "spell_menu_f3_4": self.spell_menu_f3_4.current(),
                "spell_menu_f4_1": self.spell_menu_f4_1.current(),
                "spell_menu_f4_2": self.spell_menu_f4_2.current(),
                "spell_menu_f4_3": self.spell_menu_f4_3.current(),
                "spell_menu_f4_4": self.spell_menu_f4_4.current(),
            },
            "ancient": self.ancient.current(),
            "ancient_throw": self.ancient_throw.current(),
            "broom": self.broom.current(),
            "mount_1": self.mount_1.current(),
            "mount_2": self.mount_2.current(),
            "tool": self.tool.current(),
            "playing_device": self.playing_device.current(),
            "revelio": self.revelio.current(),
            "protego": self.protego.current(),
            "inventory": self.inventory.current(),
            "gear": self.gear.current(),
            "map": self.map.current(),
            "quests": self.quests.current(),
            "challenges": self.challenges.current(),
            "talents": self.talents.current(),
            "heal": self.heal.current(),
            "alohomora": self.alohomora.current(),
            "petrificus": self.petrificus.current()
        }
        with open(resource_path("{}\\user_preferences.json".format(self.data_path)), "w+") as f:
            json.dump(self.user_preferences, f)
    
    def get_preferences(self):
        try:
            with open(resource_path("{}\\user_preferences.json".format(self.data_path)), "r") as f:
                self.user_preferences = json.load(f)
                self.spell_menu_f1_1.current(self.user_preferences["spells"]["spell_menu_f1_1"])
                self.spell_menu_f1_2.current(self.user_preferences["spells"]["spell_menu_f1_2"])
                self.spell_menu_f1_3.current(self.user_preferences["spells"]["spell_menu_f1_3"])
                self.spell_menu_f1_4.current(self.user_preferences["spells"]["spell_menu_f1_4"])
                self.spell_menu_f2_1.current(self.user_preferences["spells"]["spell_menu_f2_1"])
                self.spell_menu_f2_2.current(self.user_preferences["spells"]["spell_menu_f2_2"])
                self.spell_menu_f2_3.current(self.user_preferences["spells"]["spell_menu_f2_3"])
                self.spell_menu_f2_4.current(self.user_preferences["spells"]["spell_menu_f2_4"])
                self.spell_menu_f3_1.current(self.user_preferences["spells"]["spell_menu_f3_1"])
                self.spell_menu_f3_2.current(self.user_preferences["spells"]["spell_menu_f3_2"])
                self.spell_menu_f3_3.current(self.user_preferences["spells"]["spell_menu_f3_3"])
                self.spell_menu_f3_4.current(self.user_preferences["spells"]["spell_menu_f3_4"])
                self.spell_menu_f4_1.current(self.user_preferences["spells"]["spell_menu_f4_1"])
                self.spell_menu_f4_2.current(self.user_preferences["spells"]["spell_menu_f4_2"])
                self.spell_menu_f4_3.current(self.user_preferences["spells"]["spell_menu_f4_3"])
                self.spell_menu_f4_4.current(self.user_preferences["spells"]["spell_menu_f4_4"])
                self.ancient.current(self.user_preferences["ancient"])
                self.ancient_throw.current(self.user_preferences["ancient_throw"])
                self.broom.current(self.user_preferences["broom"])
                self.mount_1.current(self.user_preferences["mount_1"])
                self.mount_2.current(self.user_preferences["mount_2"])
                self.tool.current(self.user_preferences["tool"])
                self.playing_device.current(self.user_preferences["playing_device"])
                self.revelio.current(self.user_preferences["revelio"]),
                self.protego.current(self.user_preferences["protego"]),
                self.inventory.current(self.user_preferences["inventory"]),
                self.gear.current(self.user_preferences["gear"]),
                self.map.current(self.user_preferences["map"]),
                self.quests.current(self.user_preferences["quests"]),
                self.challenges.current(self.user_preferences["challenges"]),
                self.talents.current(self.user_preferences["talents"]),
                self.heal.current(self.user_preferences["heal"])
                self.alohomora.current(self.user_preferences["alohomora"])
                self.petrificus.current(self.user_preferences["petrificus"])
        except:
            self.spell_menu_f1_1.current(0)
            self.spell_menu_f1_2.current(0)
            self.spell_menu_f1_3.current(0)
            self.spell_menu_f1_4.current(0)
            self.spell_menu_f2_1.current(0)
            self.spell_menu_f2_2.current(0)
            self.spell_menu_f2_3.current(0)
            self.spell_menu_f2_4.current(0)
            self.spell_menu_f3_1.current(0)
            self.spell_menu_f3_2.current(0)
            self.spell_menu_f3_3.current(0)
            self.spell_menu_f3_4.current(0)
            self.spell_menu_f4_1.current(0)
            self.spell_menu_f4_2.current(0)
            self.spell_menu_f4_3.current(0)
            self.spell_menu_f4_4.current(0)
            self.ancient.current(1)
            self.ancient_throw.current(1)
            self.broom.current(1)
            self.mount_1.current(1)
            self.mount_2.current(1)
            self.tool.current(1)
            self.playing_device.current(0)
            self.revelio.current(0),
            self.protego.current(0),
            self.inventory.current(0),
            self.gear.current(0),
            self.map.current(0),
            self.quests.current(0),
            self.challenges.current(0),
            self.talents.current(0),
            self.heal.current(0)
            self.alohomora.current(0)
            self.petrificus.current(0)
            self.save_preferences(1)
        self.update_spell_order()

    def get_words_to_recognize(self):
        self.words_to_recognize_list = []
        for item in self.user_preferences["spells"].items():
            if self.all_castable_spells[item[1]] != "DISABLED":
                if ' ' in self.all_castable_spells[item[1]]:
                    self.words_to_recognize_list.append(self.all_castable_spells[item[1]].split()[0])
                else: 
                    self.words_to_recognize_list.append(self.all_castable_spells[item[1]])
        if self.user_preferences["revelio"] == 0:
            self.words_to_recognize_list.append("REVELIO")
        if self.user_preferences["protego"] == 0:
            self.words_to_recognize_list.append("PROTEGO")
        if self.user_preferences["inventory"] == 0:
            self.words_to_recognize_list.append("INVENTORY")
        if self.user_preferences["gear"] == 0:
            self.words_to_recognize_list.append("GEAR")
        if self.user_preferences["map"] == 0:
            self.words_to_recognize_list.append("MAP")
        if self.user_preferences["quests"] == 0:
            self.words_to_recognize_list.append("QUESTS")
        if self.user_preferences["challenges"] == 0:
            self.words_to_recognize_list.append("CHALLENGES")
        if self.user_preferences["talents"] == 0:
            self.words_to_recognize_list.append("TALENTS")
        if self.user_preferences["heal"] == 0:
            self.words_to_recognize_list.append("HEAL")
        if self.user_preferences["alohomora"] == 0:
            self.words_to_recognize_list.append("ALOHOMORA")
        if self.user_preferences["petrificus"] == 0:
            self.words_to_recognize_list.append("PETRIFICUS")
        if self.user_preferences["ancient"] != 0:
            self.words_to_recognize_list.append(self.ancient_options[self.user_preferences["ancient"]])
        if self.user_preferences["ancient_throw"] != 0:
            self.words_to_recognize_list.append(self.ancient_throw_options[self.user_preferences["ancient_throw"]])
        if self.user_preferences["broom"] != 0:
            self.words_to_recognize_list.append(self.broom_options[self.user_preferences["broom"]])
        if self.user_preferences["mount_1"] != 0:
            self.words_to_recognize_list.append(self.walk_mount_options[self.user_preferences["mount_1"]])
        if self.user_preferences["mount_2"] != 0:
            self.words_to_recognize_list.append(self.fly_mount_options[self.user_preferences["mount_2"]])
        if self.user_preferences["tool"] != 0:
            self.words_to_recognize_list.append(self.tool_options[self.user_preferences["tool"]])
        if "LUMOS" in self.words_to_recognize_list:
            self.words_to_recognize_list.append("NOX")
        if "WINGARDIUM" in self.words_to_recognize_list:
            self.words_to_recognize_list.append("FINITE")
        if "INVISIBLE" in self.words_to_recognize_list:
            self.words_to_recognize_list.append("VISIBLE")
        self.words_to_recognize_list.append("[unk]")
        return self.words_to_recognize_list

    def start_recognizer_thread(self):
        if self.valid_license == True:
            if self.input_device.current() != 0:
                self.casting.selected_device = self.input_device.get()
                self.casting.playing_device = self.playing_device.current()
                self.get_preferences()
                self.casting.selected_ancient = self.ancient.get()
                self.casting.selected_ancient_throw = self.ancient_throw.get()
                self.casting.selected_broom = self.broom.get()
                self.casting.selected_mount_one = self.mount_1.get()
                self.casting.selected_mount_two = self.mount_2.get()
                self.casting.selected_tool = self.tool.get()

                self.casting.words_to_recognize = self.get_words_to_recognize()

                recognizer_thread = threading.Thread(target=self.casting.start_recording, daemon=True)
                recognizer_thread.start()
                self.start_button.state(['disabled'])
                self.stop_button.state(['!disabled'])
                self.status_label.config(text="Voice Recognition is running, go play!")
                self.running = True
                error_update_thread = threading.Thread(target=self.RefreshErrorMessage, daemon=True)
                error_update_thread.start()
                progress_update_thread = threading.Thread(target=self.RefreshProgressMessage, daemon=True)
                progress_update_thread.start()
            else:
                messagebox.showerror(title="Invalid Input Device", message="Invalid input device. Please connect a microphone and then restart the program.")
        else: 
            messagebox.showerror(title="Invalid Key", message="Invalid license key. Please enter a valid key!")
            self.open_license_window(self.master)

    def RefreshErrorMessage(self):
        while(self.running):
            self.error_label.configure(text=self.casting.error_message)
            time.sleep(5)

    def RefreshProgressMessage(self):
        while(self.running):
            self.progress_label.configure(text=self.casting.progress_message)
            time.sleep(2)

    def stop_recognizer_thread(self):
        self.casting.stop_recording()
        self.start_button.state(['!disabled'])
        self.status_label.config(text="Voice Recognition stopped")
        self.running = False

class SpeechRecognition:
    def __init__(self, master):
        SetLogLevel(-1)
        self.recording = False
        self.selected_device = ""
        self.playing_device = ""
        self.keyboard = Controller()
        self.spell_keys = {}
        self.error_message = "If a spell is not working, please first check if you \nconfigured everything properly\n (Refreshes every 5 seconds) \n"
        self.progress_message = "The last casted spell name will be displayed here. \nThis allows you to check if the program is working correctly \n (Refreshes every 2 seconds) \n"
        self.gamepad = vg.VDS4Gamepad()
        self.selected_ancient = ""
        self.selected_ancient_throw = ""
        self.selected_broom = ""
        self.selected_mount_one = ""
        self.selected_mount_one = ""
        self.selected_tool = ""
        self.words_to_recognize = ""
        self.finite_slot = ""
        
    def start_recording(self):
        self.q = queue.Queue()
        # Get the selected device name
        # Get the device info for the selected device
        device_info = next(d for d in sd.query_devices() if d["name"] == self.selected_device)
        self.words_to_recognize = ' '.join(map(str, self.words_to_recognize))
        self.samplerate = int(device_info["default_samplerate"])
        self.model = Model("mods")
        self.rec = KaldiRecognizer(self.model, self.samplerate, '''["{}"]'''.format(self.words_to_recognize))
        if "WINGARDIUM" in self.words_to_recognize:
            self.finite_slot = self.spell_keys["WINGARDIUM LEVIOSA"]["slot"]
        self.audio_loop(device_info)
    
    def audio_loop(self, device_info):
        print("Ready for inputs!")
        self.recording = True
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, device=device_info["index"], dtype="int16", channels=1, callback=self.callback):
            while self.recording:
                data = self.q.get()        

                if self.rec.AcceptWaveform(data):
                    result_str = self.rec.Result()
                    result_dict = json.loads(result_str)
                    if (result_dict['text'] != "[unk]") & (result_dict['text'] != ""):
                        if ' ' in result_dict['text'] and ('WINGARDIUM' in result_dict['text'] or 'ARRESTO' in result_dict['text'] or 'AVADA' in result_dict['text']):
                            spells = result_dict['text'].split(' ')[0]
                            if spells != '[unk]':
                                self.cast_spell(spells)
                        elif ' ' in result_dict['text']:
                            spells = result_dict['text'].split(' ')
                            for spell in spells:
                                if spell != '[unk]':
                                    self.cast_spell(spell)
                                    time.sleep(0.75)
                        else:
                            spells = result_dict['text']
                            if spells != '[unk]':
                                self.cast_spell(spells)

    def cast_spell(self, spell_name):
        match spell_name:
            case "AVADA": spell_name = "AVADA KEDAVRA"
            case "WINGARDIUM": spell_name = "WINGARDIUM LEVIOSA"
            case "ARRESTO": spell_name = "ARRESTO MOMENTUM"
            case "NOX": spell_name = "LUMOS"
            case "VISIBLE": spell_name = "INVISIBLE"
        spell_data = self.spell_keys.get('{}'.format(spell_name))
        self.progress_message = "Casting {}".format(spell_name)   
        if spell_data != None:
            card = spell_data["card"]
            slot = spell_data["slot"]
            if self.playing_device == 0:
                match card:
                    case "f1":
                        self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                        self.gamepad.update()
                        time.sleep(0.025)
                    case "f2":
                        self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                        self.gamepad.update()
                        time.sleep(0.025)
                    case "f3":
                        self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                        self.gamepad.update()
                        time.sleep(0.025)
                    case "f4":
                        self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
                        self.gamepad.update()
                        time.sleep(0.025)
                        self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                        self.gamepad.update()
                        time.sleep(0.025)
                if spell_name != "WINGARDIUM LEVIOSA":
                    match slot:
                        case "1":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                            self.gamepad.update()
                        case "2":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                            self.gamepad.update()
                        case "3":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                            self.gamepad.update()
                        case "4":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                            self.gamepad.update() 
                elif spell_name == "WINGARDIUM LEVIOSA":
                    match slot:
                        case "1":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                            self.gamepad.update()
                        case "2":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                            self.gamepad.update()
                        case "3":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
                            self.gamepad.update()
                        case "4":
                            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                            self.gamepad.update()
                            time.sleep(0.025)
                            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                            self.gamepad.update() 
            elif self.playing_device == 1:
                match card:
                    case "f1":
                        self.keyboard.press(Key.f1)
                        self.keyboard.release(Key.f1)
                    case "f2":
                        self.keyboard.press(Key.f2)
                        self.keyboard.release(Key.f2)
                    case "f3":
                        self.keyboard.press(Key.f3)
                        self.keyboard.release(Key.f3)
                    case "f4":
                        self.keyboard.press(Key.f4)
                        self.keyboard.release(Key.f4)
                match slot:
                    case "1":
                        time.sleep(0.025)
                        self.keyboard.press('1')
                        self.keyboard.release('1')
                    case "2":
                        time.sleep(0.025)
                        self.keyboard.press('2')
                        self.keyboard.release('2')
                    case "3":
                        time.sleep(0.025)
                        self.keyboard.press('3')
                        self.keyboard.release('3')
                    case "4":
                        time.sleep(0.025)
                        self.keyboard.press('4')
                        self.keyboard.release('4')
        elif spell_name == "FINITE":
            if self.playing_device == 0:
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT)
                time.sleep(0.025)
                self.gamepad.update() 
            elif self.playing_device == 1:
                self.keyboard.press('{}'.format(self.finite_slot))
                self.keyboard.release('{}'.format(self.finite_slot))
        elif spell_name == "REVELIO":
            if self.playing_device == 0:
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
                self.gamepad.update() 
                time.sleep(0.025)
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('r')
                self.keyboard.release('r')
        elif spell_name == "PROTEGO":
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('q')
                self.keyboard.release('q')
        elif spell_name == "HEAL":
            if self.playing_device == 0:
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('g')
                self.keyboard.release('g')
        elif spell_name == "ALOHOMORA" or spell_name == "PETRIFICUS":
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('f')
                self.keyboard.release('f')
        elif spell_name == self.selected_broom:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
                time.sleep(0.5)
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(Key.tab)
                time.sleep(0.5)
                self.keyboard.press('3')
                self.keyboard.release('3')
                self.keyboard.release(Key.tab)
        elif spell_name == self.selected_mount_one:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
                time.sleep(0.5)
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(Key.tab)
                time.sleep(0.5)
                self.keyboard.press('1')
                self.keyboard.release('1')
                self.keyboard.release(Key.tab)
        elif spell_name == self.selected_mount_two:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
                time.sleep(0.5)
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(Key.tab)
                time.sleep(0.5)
                self.keyboard.press('2')
                self.keyboard.release('2')
                self.keyboard.release(Key.tab)
        elif spell_name == self.selected_tool:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(Key.tab)
                time.sleep(0.025)
                self.keyboard.release(Key.tab)
        elif spell_name == self.selected_ancient:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(x)
                time.sleep(0.025)
                self.keyboard.release(x)
        elif spell_name == self.selected_ancient_throw:
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)
                self.gamepad.update()
                time.sleep(0.025)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press(y)
                time.sleep(0.025)
                self.keyboard.release(y)
        elif spell_name == "INVENTORY":
            self.keyboard.press('l')
            self.keyboard.release('l')
        elif spell_name == "GEAR":
            self.keyboard.press('i')
            self.keyboard.release('i')
        elif spell_name == "MAP":
            self.keyboard.press('m')
            self.keyboard.release('m')
        elif spell_name == "CHALLENGES":
            self.keyboard.press('u')
            self.keyboard.release('u')
        elif spell_name == "QUESTS":
            self.keyboard.press('j')
            self.keyboard.release('j')
        elif spell_name == "TALENTS":
            self.keyboard.press('n')
            self.keyboard.release('n')
        else:
            self.error_message = "Error while trying to cast {}, \nplease check if you configured the spell in the inputs.".format(spell_name)              

    def stop_recording(self):
        self.recording = False

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(resource_path("Icon.ico"))
    app = WizardVoiceGUI(root)
    root.mainloop()
