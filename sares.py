import speech_recognition as sr
import pyttsx3
import subprocess
import tkinter as tk
import threading
import os
import time
import json
import math
import pyautogui
import cv2
import pytesseract
import ollama
import pvporcupine
import pyaudio
import struct
MIC_INDEX = 4


import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource (works for dev and PyInstaller) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ---------------- MEMORY ---------------- #

def clean_command(text):
    text = text.lower()
    text = text.replace(".", "")
    text = text.replace("?", "")
    text = text.replace(",", "")
    text = text.replace("please", "")
    text = text.replace("can you", "")
    text = text.replace("could you", "")
    text = text.strip()
    return text

def set_state(new_state):
    global state
    state = new_state

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

# ---------------- AI ---------------- #

conversation_memory = []

def ask_ai(prompt):
    conversation_memory.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model='mistral',
            messages=conversation_memory
        )
        reply = response['message']['content']
    except:
        reply = "Local AI not responding."

    conversation_memory.append({"role": "assistant", "content": reply})
    return reply

def ai_agent_decision(command):

    prompt = f"""
Decide action for this command:
{command}

Return only:

ACTION: open_app / search_google / open_website / type / talk
DATA: info
"""

    try:
        response = ollama.chat(
            model='mistral',
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except:
        return "ACTION: talk\nDATA: " + command

# ---------------- APPS ---------------- #

def get_installed_apps():
    apps = {}
    for f in os.listdir("/Applications"):
        if f.endswith(".app"):
            name = f.replace(".app","").lower()
            apps[name] = f.replace(".app","")
    return apps

INSTALLED_APPS = get_installed_apps()

def open_app(app_name):

    app_name = app_name.lower().strip()

    best_match = None

    for installed in INSTALLED_APPS:
        if app_name in installed:
            best_match = INSTALLED_APPS[installed]
            break

    if best_match:
        update_ui("SARES: Opening " + best_match)
        speak("Opening " + best_match)
        subprocess.run(["open", "-a", best_match])
    else:
        update_ui("SARES: App not found")
        speak("I could not find that app")

# ---------------- BROWSER ---------------- #

def open_and_search(query):
    subprocess.run(["open", "-a", "Google Chrome"])
    time.sleep(3)
    pyautogui.write(query)
    pyautogui.press("enter")

# ---------------- FILE ---------------- #

def create_and_write_file(command):
    try:
        parts = command.split("file")
        filename = parts[1].split()[0] + ".txt"
        content = command.split("write")[-1].strip()

        with open(filename, "w") as f:
            f.write(content)

        subprocess.run(["open", filename])
        speak(f"{filename} created")
    except:
        speak("Could not create file")

def write_to_file(command):
    try:
        content = command.split("write")[1].strip()
        with open("notes.txt", "a") as f:
            f.write(content + "\n")
        speak("Written to file")
    except:
        speak("Could not write")

# ---------------- VISION ---------------- #

def find_text_on_screen(target):
    screenshot = pyautogui.screenshot()
    screenshot.save("screen.png")

    img = cv2.imread("screen.png")
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    for i in range(len(data['text'])):
        word = data['text'][i].lower()
        if target.lower() in word:
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            return x + w//2, y + h//2

    return None

def smart_click(target):
    pos = find_text_on_screen(target)
    if pos:
        pyautogui.click(pos[0], pos[1])
        speak("Clicking " + target)
    else:
        speak("Text not found on screen")

# ---------------- SPEECH ---------------- #

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    set_state("speaking")
    update_ui("SARES: " + text)

    engine.say(text)
    engine.runAndWait()

    set_state("idle")

import sounddevice as sd
from scipy.io.wavfile import write
import whisper

whisper_model = whisper.load_model("base")

import sounddevice as sd
from scipy.io.wavfile import write
import whisper

whisper_model = whisper.load_model("base")

def listen():

    try:
        set_state("listening")

        fs = 16000
        seconds = 4

        recording = sd.rec(
            int(seconds * fs),
            samplerate=fs,
            channels=1,
            device=MIC_INDEX
        )

        sd.wait()
        write("voice.wav", fs, recording)

        set_state("thinking")

        result = whisper_model.transcribe("voice.wav")
        command = result["text"].lower().strip()

        command = clean_command(command)

        update_ui("You: " + command)

        return command

    except:
        set_state("idle")
        return ""
# ---------------- COMMAND ---------------- #

def run_command(command):
    print("FINAL COMMAND:", command)
    update_ui("Command → " + command)

    try:
        command = command.lower().strip()

        # -------- OPEN ANY APP --------
        # -------- OPEN APP --------
        if command.startswith("open "):
            app = command.replace("open ", "").strip()
            open_app(app)
            return

        if command.startswith("launch "):
            app = command.replace("launch ", "").strip()
            open_app(app)
            return

        if command.startswith("start "):
            app = command.replace("start ", "").strip()
            open_app(app)
            return

        # -------- SEARCH --------
        if "search" in command:
            query = command.replace("search", "").strip()
            open_and_search(query)
            return

        # -------- CLICK --------
        if "click" in command:
            target = command.replace("click", "").strip()
            smart_click(target)
            return

        # -------- FILE --------
        if "create file" in command:
            create_and_write_file(command)
            return

        if "write" in command:
            write_to_file(command)
            return

        # -------- MEMORY --------
        if "remember that" in command:
            data = command.replace("remember that", "")
            memory["note"] = data
            save_memory(memory)
            speak("I will remember that")
            return

        if "what do you remember" in command:
            speak(memory.get("note", "Nothing yet"))
            return

        # -------- AI CHAT --------
        reply = ask_ai(command)
        speak(reply)

    except Exception as e:
        print("Error in run_command:", e)
        speak("Something went wrong")

# ---------------- WAKE WORD ---------------- #

ACCESS_KEY = "YOUR ACCESS KEY"

def wait_for_wake_word():

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[resource_path("Buddy.ppn")]
    )

    pa = pyaudio.PyAudio()

    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    while True:
        pcm = stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h"*porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            porcupine.delete()
            return

# ---------------- LOOP ---------------- #

def assistant_loop():

    speak("SARES running")

    while True:

        try:
            print("Waiting for wake word...")
            set_state("idle")

            wait_for_wake_word()

            speak("Yes")

            # Listen with timeout protection
            start_time = time.time()

            command = listen()

            # If nothing heard within 10 sec → go back to wake
            if command == "" or (time.time() - start_time > 10):
                speak("No command received")
                continue

            run_command(command)

            # After task → go back to wake word
            print("Task done, returning to wake mode")

        except Exception as e:
            print("Main loop error:", e)
            speak("Returning to standby")
            continue

# ---------------- UI ---------------- #

def start_ui():
    global window, canvas, circle, chat_box, state

    state = "idle"

    window = tk.Tk()
    window.overrideredirect(True)
    window.geometry("420x500+900+300")
    window.configure(bg="black")
    window.attributes("-topmost", True)
    window.attributes("-alpha", 0.95)

    canvas = tk.Canvas(window, width=420, height=250, bg="black", highlightthickness=0)
    canvas.pack()

    circle = canvas.create_oval(160, 60, 260, 160, fill="cyan", outline="")

    # Chat box (holographic console)
    chat_box = tk.Text(
        window,
        bg="black",
        fg="cyan",
        font=("Courier", 12),
        insertbackground="cyan",
        bd=0
    )
    chat_box.pack(fill="both", expand=True)

    def animate():
        colors = {
            "idle": "cyan",
            "listening": "green",
            "thinking": "purple",
            "speaking": "orange"
        }

        color = colors.get(state, "cyan")

        size = 40 + 10 * math.sin(time.time()*3)
        canvas.coords(circle, 210-size, 110-size, 210+size, 110+size)
        canvas.itemconfig(circle, fill=color)

        window.after(50, animate)

    animate()

    def drag(event):
        window.geometry(f"+{event.x_root}+{event.y_root}")

    canvas.bind("<B1-Motion>", drag)

    return window

def update_ui(text):
    chat_box.insert("end", text + "\n")
    chat_box.see("end")

# ---------------- MAIN ---------------- #

def start_assistant():
    thread = threading.Thread(target=assistant_loop)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    window = start_ui()
    start_assistant()
    window.mainloop()