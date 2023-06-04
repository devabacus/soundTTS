import requests
import shutil
import time
import os
import re

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def post_request(text, language):
    url = "https://api.soundoftext.com/sounds"
    data = {
        "engine": "Google",
        "data": {
            "text": text,
            "voice": language
        }
    }
    response = requests.post(url, json=data)
    return response

def get_request(sound_url):
    while True:
        response = requests.get(sound_url)
        if response.json()["status"] == "Done":
            return response
        elif response.json()["status"] == "Error":
            print("Error occurred: ", response.json()["message"])
            return None
        time.sleep(2)

def download_file(download_url, file_path):
    response = requests.get(download_url, stream=True)
    with open(file_path, "wb") as sound_file:
        shutil.copyfileobj(response.raw, sound_file)
    return os.path.basename(file_path)

def download_sound(text, language, output_folder):
    response = post_request(text, language)
    if response.status_code != 200:
        print("Error occurred: ", response.json()["message"])
        return None

    sound_id = response.json()["id"]
    sound_url = f"https://api.soundoftext.com/sounds/{sound_id}"

    response = get_request(sound_url)
    if not response:
        return None

    download_url = response.json()["location"]
    filename = clean_filename(f"{text[:30].replace(' ', '_')}") + '.mp3'
    file_path = f"{output_folder}/{filename}"

    return download_file(download_url, file_path)

if __name__ == "__main__":
    # For testing purposes
    text = "Do you want to know the names of the dishes we make?"
    language = "en-US"
    output_folder = os.getcwd()  # current directory

    filename = download_sound(text, language, output_folder)
    if filename:
        print(f"Successfully downloaded sound file: {filename}")
    else:
        print("Failed to download sound file.")
