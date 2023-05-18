import requests
import shutil
import time
import os
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


script_dir = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    # Change these to suitable values for testing
    text = "මම යන්නේ බබාට සෙල්ලම් කරන්න"
    language = "si"
    output_folder = script_dir  # directory of the script

    filename = download_sound(text, language, output_folder)

    if filename:
        print(f"Successfully downloaded sound file: {filename}")
    else:
        print("Failed to download sound file.")