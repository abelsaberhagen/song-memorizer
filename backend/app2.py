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