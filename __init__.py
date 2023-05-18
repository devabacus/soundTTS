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

from .donwload_mp3 import download_sound

def on_edit_action(browser):
    selected_cards = browser.selectedCards()
    
    progress_dialog = QProgressDialog("Processing cards...", "", 0, len(selected_cards), browser)
    progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.setWindowTitle("Please Wait")
    progress_dialog.setCancelButton(None)  # Disallow canceling
    progress_dialog.setMinimumDuration(0)
    progress_dialog.show()  # Make dialog visible immediately

    output_folder = os.path.join(mw.pm.profileFolder(), "collection.media")

    for i, card_id in enumerate(selected_cards):
        card = mw.col.getCard(card_id)
        note = card.note()

        # Process the Front field
        if "]" not in note.fields[0]:  # Assuming Front is the first field
            front_text = note.fields[0]
            language = "en-US"
            filename = download_sound(front_text, language, output_folder)
            if filename:
                audio_tag = f"[sound:{filename}]"
                note.fields[0] += audio_tag

        # Process the Back field
        if "]" not in note.fields[1]:  # Assuming Back is the second field
            back_text = note.fields[1].replace('&nbsp;', ' ')
            language = "si"
            filename = download_sound(back_text, language, output_folder)
            if filename:
                audio_tag = f"[sound:{filename}]"
                note.fields[1] += audio_tag

        note.flush()
        progress_dialog.setValue(i+1)
        QCoreApplication.processEvents()  

def setup_menu_item(browser):
    action = QAction("Add TTS to Front and Back", browser)
    action.triggered.connect(partial(on_edit_action, browser))
    browser.form.menuEdit.addAction(action)

addHook("browser.setupMenus", setup_menu_item)
