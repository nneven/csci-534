import os
import librosa
import logging
import numpy as np
from flask_cors import CORS
from flask import Flask, request, jsonify
from config.default import (
    extract_lyrics,
    extract_themes,
    # extract_emotion,
    # generate_prompts,
    generate_images,
    # GPT_PROMPT,
)
from config.shashank import extract_emotion
from config.nicolas import generate_prompts, GPT_PROMPT

app = Flask(__name__)
CORS(app)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

@app.route("/get_images", methods=["post"])
def get_cover():
    
    if "song" not in request.files:
        return "No song file in request", 400

    file = request.files["song"]
    file.save(file.filename)
    logging.info(f"Saved file: {file.filename}")

    if file.filename.split(".")[-1] != "mp3":
        return "Invalid file type", 400

    y, sr = librosa.load(file.filename)

    duration = librosa.get_duration(y=y, sr=sr)
    mid_quartiles = np.percentile(np.arange(duration), [25, 75])
    start_time = np.random.uniform(low=mid_quartiles[0], high=mid_quartiles[1]-30)
    y = y[int(start_time*sr):int((start_time+30)*sr)]



    lyrics = extract_lyrics(file.filename)
    logging.info(f"Extracted lyrics: {lyrics}")

    themes = extract_themes(lyrics)
    logging.info(f"Extracted themes: {themes}")

    emotion = extract_emotion(y, sr)
    logging.info(f"Extracted emotion: {emotion}")

    image_prompts = generate_prompts(themes, emotion, GPT_PROMPT, num_prompts=2)
    logging.info(f"Generated image prompts: {image_prompts}")

    images = generate_images(image_prompts, num_images=2)
    logging.info(f"Generated images: {images}")

    os.remove(file.filename)
    logging.info(f"Removed file: {file.filename}")

    return jsonify(images), 200


if __name__ == "__main__":
    app.run(debug=True)
