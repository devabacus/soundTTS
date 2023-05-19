from aqt import mw
from .donwload_mp3 import download_sound

def process_card(card_id, output_folder):
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
