import queue
import sounddevice as sd
import json
from pynput.keyboard import Key, Controller
import time
import vgamepad as vg

from vosk import Model, KaldiRecognizer, SetLogLevel

class SpeechRecognition:
    def __init__(self, master):
        SetLogLevel(-1)
        self.recording = False
        self.selected_device = ""
        self.playing_device = ""
        self.keyboard = Controller()
        self.spell_keys = {}
        self.error_message = "This tool is perfect, errors are 100% your fault! :D \n (Refreshes every 10 seconds) \n\n\n\n\n\n\n\n"
        self.gamepad = vg.VDS4Gamepad()
        
    def start_recording(self):
        self.q = queue.Queue()
        # Get the selected device name
        # Get the device info for the selected device
        device_info = next(d for d in sd.query_devices() if d["name"] == self.selected_device)

        self.samplerate = int(device_info["default_samplerate"])
        self.model = Model("speech/mods")
        self.rec = KaldiRecognizer(self.model, self.samplerate, 
        '''["ACCIO", "ARRESTO", "AVADA", "BOMBARDA", "CONFRINGO", "CRUCIO", "DEPULSO", "DESCENDO", "DIFFINDO", "EXPELLIARMUS", "FLIPENDO", "GLACIUS", "IMPERIO", 
            "INCENDIO", "INVISIBLE", "LEVIOSO", "LUMOS", "PROTEGO", "REPARO", "REVELIO", "TRANSFORM", "WINGARDIUM", "[unk]"]''')

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
                    print(result_dict['text'])
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
        spell_data = self.spell_keys.get('{}'.format(spell_name))
        print("casting", spell_name)
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
                        self.keyboard.press('1')
                        self.keyboard.release('1')
                    case "2":
                        self.keyboard.press('2')
                        self.keyboard.release('2')
                    case "3":
                        self.keyboard.press('3')
                        self.keyboard.release('3')
                    case "4":
                        self.keyboard.press('4')
                        self.keyboard.release('4')
        elif spell_name == "REVELIO":
            if self.playing_device == 0:
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
                self.gamepad.update()
                time.sleep(0.02)
                self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('r')
                self.keyboard.release('r')
        elif spell_name == "PROTEGO":
            if self.playing_device == 0:
                self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.update()
                time.sleep(0.02)
                self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)
                self.gamepad.update()
            elif self.playing_device == 1:
                self.keyboard.press('q')
                self.keyboard.release('q')
        else:
            self.error_message = "Error while trying to cast {}, \nplease check if you configured the spell in the inputs.".format(spell_name)              

    def stop_recording(self):
        self.recording = False

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

