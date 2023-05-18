from aqt import mw, dialogs
from aqt.utils import showInfo, askUser, showText, tooltip
from anki.hooks import addHook
from aqt.qt import QAction, QProgressDialog, QCoreApplication
from PyQt6.QtCore import Qt
import requests
import shutil
import time
import os
from functools import partial
import re

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_sound(text, language, output_folder):
    url = "https://api.soundoftext.com/sounds"
    data = {
        "engine": "Google",
        "data": {
            "text": text,
            "voice": language
        }
    }

    response = requests.post(url, json=data)
    response_json = response.json()

    if response.status_code != 200:
        print("Error occurred: ", response_json["message"])
        return None

    sound_id = response_json["id"]
    sound_url = f"https://api.soundoftext.com/sounds/{sound_id}"

    while True:
        response = requests.get(sound_url)
        response_json = response.json()

        if response_json["status"] == "Done":
            download_url = response_json["location"]
            break
        elif response_json["status"] == "Error":
            print("Error occurred: ", response_json["message"])
            return None

        time.sleep(2)

    response = requests.get(download_url, stream=True)
    filename = clean_filename(f"{text[:30].replace(' ', '_')}") + '.mp3'
    file_path = f"{output_folder}/{filename}"

    with open(file_path, "wb") as sound_file:
        shutil.copyfileobj(response.raw, sound_file)

    return filename

def on_edit_action(browser):
    selected_cards = browser.selectedCards()
    
    progress_dialog = QProgressDialog("Processing cards...", "", 0, len(selected_cards), browser)
    progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.setWindowTitle("Please Wait")
    progress_dialog.setCancelButton(None)  # Disallow canceling
    progress_dialog.setMinimumDuration(0)
    progress_dialog.show()  # Make dialog visible immediately

    output_folder = os.path.join(mw.pm.profileFolder(), "collection.media")
    language = "en-US"

    for i, card_id in enumerate(selected_cards):
        card = mw.col.getCard(card_id)
        note = card.note()
        front_text = note.fields[0]

        filename = download_sound(front_text, language, output_folder)

        if filename:
            audio_tag = f"[sound:{filename}]"
            note.fields[0] += audio_tag
            note.flush()

        progress_dialog.setValue(i+1)
        QCoreApplication.processEvents()  # Update the UI

def setup_menu_item(browser):
    action = QAction("Add TTS to Front", browser)
    action.triggered.connect(partial(on_edit_action, browser))
    browser.form.menuEdit.addAction(action)

addHook("browser.setupMenus", setup_menu_item)
