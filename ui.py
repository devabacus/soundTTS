from aqt import mw
from aqt.qt import QAction, QProgressDialog, QCoreApplication
from PyQt6.QtCore import Qt
from anki.hooks import addHook
from functools import partial
import os

from .logic import process_card

def on_edit_action(browser):
    selected_cards = browser.selectedCards()
    
    progress_dialog = QProgressDialog("Processing cards...", "", 0, len(selected_cards), browser)
    # progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress_dialog.setWindowTitle("Please Wait")
    progress_dialog.setCancelButton(None)  # Disallow canceling
    progress_dialog.setMinimumDuration(0)
    progress_dialog.show()  # Make dialog visible immediately

    output_folder = os.path.join(mw.pm.profileFolder(), "collection.media")

    for i, card_id in enumerate(selected_cards):
        process_card(card_id, output_folder)
        progress_dialog.setValue(i+1)
        QCoreApplication.processEvents()  

def setup_menu_item(browser):
    action = QAction("Add TTS to Front and Back", browser)
    action.triggered.connect(partial(on_edit_action, browser))
    browser.form.menuEdit.addAction(action)

def on_browser_context_menu(browser, menu):
    action = QAction("Add TTS to Front and Back", browser)
    action.triggered.connect(partial(on_edit_action, browser))
    menu.addAction(action)
