import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from voice_to_text import VoiceToText

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
CORS(app)

PRESETS_FOLDER = os.path.join(os.path.dirname(__file__), "../presets")
os.makedirs(PRESETS_FOLDER, exist_ok=True)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for f in os.listdir(UPLOAD_FOLDER):
    os.remove(os.path.join(UPLOAD_FOLDER, f))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_AUDIO = {"mp3", "wav", "ogg", "m4a", "webm"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_AUDIO


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file  = request.files["audio"]
    lyrics_text = request.form.get("lyrics", "")

    if not allowed_file(audio_file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(audio_file.filename)}"
    audio_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    unwanted = ['.', ',', '!', '?']
    lines = []
    for line in lyrics_text.split("\n"):
        for c in unwanted:
            line = line.replace(c, "")
        line = line.strip().lower()
        if line:
            lines.append(line)

    return jsonify({"filename": filename, "lyrics": lines})


@app.route("/presets")
def list_presets():
    songs = []
    for fname in sorted(os.listdir(PRESETS_FOLDER)):
        name, ext = os.path.splitext(fname)
        if ext == ".txt":
            songs.append({"id": name, "name": name.replace("_", " ").title()})
    return jsonify(songs)


@app.route("/presets/<song_id>")
def load_preset(song_id):
    txt_path = os.path.join(PRESETS_FOLDER, f"{song_id}.txt")
    if not os.path.exists(txt_path):
        return jsonify({"error": "Preset not found"}), 404

    with open(txt_path, encoding="utf-8") as f:
        lyrics_text = f.read()

    audio_file = next(
        (f for f in os.listdir(PRESETS_FOLDER)
         if os.path.splitext(f)[0] == song_id and os.path.splitext(f)[1] != ".txt"),
        None
    )

    unwanted = ['.', ',', '!', '?']
    lines = []
    for line in lyrics_text.split("\n"):
        for c in unwanted:
            line = line.replace(c, "")
        line = line.strip().lower()
        if line:
            lines.append(line)

    return jsonify({
        "lyrics": lines,
        "audio_url": f"/presets/{song_id}/audio" if audio_file else None
    })


@app.route("/presets/<song_id>/audio")
def serve_preset_audio(song_id):
    audio_file = next(
        (f for f in os.listdir(PRESETS_FOLDER)
         if os.path.splitext(f)[0] == song_id and os.path.splitext(f)[1] != ".txt"),
        None
    )
    if not audio_file:
        return jsonify({"error": "Audio not found"}), 404
    return send_from_directory(PRESETS_FOLDER, audio_file)


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/check", methods=["POST"])
def check():
    if "audio_recording" not in request.files:
        return jsonify({"error": "No recording provided"}), 400

    recording = request.files["audio_recording"]
    expected  = request.form.get("expected_line", "").strip().lower()

    rec_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        f"rec_{uuid.uuid4().hex[:8]}.webm"
    )
    recording.save(rec_path)

    vt = VoiceToText()
    transcription = vt.transcribe_file(rec_path)

    try:
        os.remove(rec_path)
    except Exception:
        pass

    if transcription is None:
        return jsonify({
            "correct":       False,
            "feedback":      "Couldn't hear that, try again!",
            "transcription": ""
        })

    spoken  = transcription.strip().lower()
    correct = spoken == expected

    return jsonify({
        "correct":       correct,
        "feedback":      "✅ Correct!" if correct else "❌ Not quite, try again!",
        "transcription": spoken
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)