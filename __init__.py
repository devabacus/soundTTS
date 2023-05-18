from aqt import mw, dialogs
from aqt.utils import showInfo, askUser, showText, tooltip
from anki.hooks import addHook
from aqt.qt import QAction, QProgressDialog, QCoreApplication
from PyQt6.QtCore import Qt
import requests
import shutil
import time
import os

progress_dialog = None

def download_sound(text, language, output_folder, progress_callback):
    # Step 1: Send a POST request to the API to request the sound file
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

    # Step 2: Retrieve the sound file using the sound ID
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

    # Step 3: Download the sound file and save it locally
    response = requests.get(download_url, stream=True)
    filename = f"{text[:30].replace(' ', '_').replace('?', '')}.mp3"
    file_path = f"{output_folder}/{filename}"

    with open(file_path, "wb") as sound_file:
        shutil.copyfileobj(response.raw, sound_file)

    # Notify about the progress
    progress_callback()

    return filename


def on_edit_action(browser):
    selected_cards = browser.selectedCards()

    # Choose your language and output_folder accordingly
    output_folder = os.path.join(mw.pm.profileFolder(), "collection.media")
    language = "en-US"

    
    
    for i, card_id in enumerate(selected_cards):
        card = mw.col.getCard(card_id)
        note = card.note()
        front_text = note.fields[0]  # Assuming Front is the first field

        def progress_callback():
            progress_dialog.setValue(i + 1)
            QCoreApplication.processEvents()  # Update the UI

        filename = download_sound(front_text, language, output_folder, progress_callback)

        if filename:
            # Generate audio tag for the mp3 file
            audio_tag = f"[sound:{filename}]"
            # Append the audio tag to the Front field
            note.fields[0] += audio_tag
            note.flush()
        else:
            showInfo(f"Could not download sound file for card {card_id}.")

    if progress_dialog:
        while progress_dialog.value() < progress_dialog.maximum():
            QCoreApplication.processEvents()  # Update the UI

def setup_menu_item(browser):
    action = QAction("Add TTS to Front", browser)
    action.triggered.connect(lambda _, b=browser: on_edit_action(b))
    browser.form.menuEdit.addAction(action)
    

addHook("browser.setupMenus", setup_menu_item)