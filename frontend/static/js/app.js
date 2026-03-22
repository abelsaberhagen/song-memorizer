const API = "http://127.0.0.1:5000";
 
// ── DOM refs ──────────────────────────────────────────────────────────────────
const uploadScreen = document.getElementById("upload-screen");
const karaokeScreen = document.getElementById("karaoke-screen");
const audioInput   = document.getElementById("audio-input");
const audioDrop    = document.getElementById("audio-drop");
const audioLabel   = document.getElementById("audio-label");
const lyricsInput  = document.getElementById("lyrics-input");
const startBtn     = document.getElementById("start-btn");
const lineCounter  = document.getElementById("line-counter");
const stageLabel   = document.getElementById("stage-label");
const micRing      = document.getElementById("mic-ring");
const ringProgress = document.getElementById("ring-progress");
const listenBtn    = document.getElementById("listen-btn");
const feedbackBox  = document.getElementById("feedback-box");
const progressBar  = document.getElementById("progress-bar");
const backBtn      = document.getElementById("back-btn");
const presetList   = document.getElementById("preset-list");
 
// ── State ─────────────────────────────────────────────────────────────────────
let lyrics         = [];
let lineIndex      = 0;
let audioFile      = null;
let mediaRecorder  = null;
let recordedChunks = [];
let isRecording    = false;
let ringAnimFrame  = null;
let ringStart      = null;
const RING_CIRCUM  = 339.3;
const MAX_RECORD_MS = 10000; // auto-stop after 10 seconds
 
// ── Upload screen ─────────────────────────────────────────────────────────────
audioInput.addEventListener("change", () => {
  audioFile = audioInput.files[0];
  if (audioFile) {
    audioLabel.textContent = `✓ ${audioFile.name}`;
    audioDrop.classList.add("has-file");
  }
  updateStartBtn();
});
 
lyricsInput.addEventListener("input", updateStartBtn);
 
function updateStartBtn() {
  startBtn.disabled = !(audioFile && lyricsInput.value.trim().length > 0);
}
 
startBtn.addEventListener("click", async () => {
  startBtn.textContent = "Uploading...";
  startBtn.disabled = true;
 
  const formData = new FormData();
  formData.append("audio", audioFile);
  formData.append("lyrics", lyricsInput.value);
 
  try {
    const res  = await fetch(`${API}/upload`, { method: "POST", body: formData });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
 
    lyrics    = data.lyrics;
    lineIndex = 0;
    showKaraokeScreen();
 
  } catch (err) {
    alert("Upload failed: " + err.message);
    startBtn.textContent = "LET'S GO →";
    startBtn.disabled = false;
  }
});
 
// ── Karaoke screen ────────────────────────────────────────────────────────────
function showKaraokeScreen() {
  uploadScreen.classList.remove("active");
  karaokeScreen.classList.add("active");
  renderState();
}
 
function renderState() {
  hideFeedback();
  setRingState("idle");
  listenBtn.classList.remove("active");
  listenBtn.disabled = false;
  listenBtn.textContent = "TAP TO SING";
 
  if (lineIndex >= lyrics.length) {
    lineCounter.textContent = "🎉 Complete!";
    stageLabel.textContent  = "You finished the whole song!";
    listenBtn.disabled = true;
    progressBar.style.width = "100%";
    return;
  }
 
  lineCounter.textContent = `Line ${lineIndex + 1} of ${lyrics.length}`;
  stageLabel.textContent  = "Tap to sing";
  progressBar.style.width = `${(lineIndex / lyrics.length) * 100}%`;
}
 
// ── Recording ─────────────────────────────────────────────────────────────────
listenBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});
 
function playStartBeep() {
  return new Promise(resolve => {
    const ctx  = new AudioContext();
    const osc  = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.4, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.3);
    osc.onended = () => { ctx.close(); resolve(); };
  });
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder  = new MediaRecorder(stream);
 
    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };
 
    mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop());
      submitRecording();
    };
 
    await playStartBeep();
 
    mediaRecorder.start();
    isRecording = true;
 
    listenBtn.textContent = "DONE SINGING";
    listenBtn.classList.add("active");
    stageLabel.textContent = "Listening...";
    setRingState("listening");
    startRingAnimation();
 
  } catch (err) {
    alert("Microphone access denied — please allow mic access and try again.");
  }
}
 
function stopRecording() {
  if (mediaRecorder && isRecording) {
    isRecording = false;
    mediaRecorder.stop();
    listenBtn.disabled = true;
    listenBtn.textContent = "Checking...";
    stageLabel.textContent = "Processing...";
    stopRingAnimation();
  }
}
 
async function submitRecording() {
  const blob = new Blob(recordedChunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("audio_recording", blob, "singing.webm");
  formData.append("expected_line", lyrics[lineIndex]);
 
  try {
    const res    = await fetch(`${API}/check`, { method: "POST", body: formData });
    const result = await res.json();
 
    showFeedback(result);
    setRingState(result.correct ? "correct" : "wrong");
 
    if (result.correct) {
      setTimeout(() => { lineIndex++; renderState(); if (lineIndex < lyrics.length) startRecording(); }, 1400);
    } else {
      setTimeout(startRecording, 2200);
    }
 
  } catch (err) {
    showFeedback({ correct: false, feedback: "Could not reach server." });
    setRingState("wrong");
    setTimeout(renderState, 2000);
  }
}
 
// ── Ring animation ────────────────────────────────────────────────────────────
function startRingAnimation() {
  ringStart = performance.now();
  function step(now) {
    const fraction = Math.min((now - ringStart) / MAX_RECORD_MS, 1);
    ringProgress.style.strokeDashoffset = RING_CIRCUM * (1 - fraction);
    if (fraction < 1 && isRecording) {
      ringAnimFrame = requestAnimationFrame(step);
    } else if (fraction >= 1 && isRecording) {
      stopRecording(); // auto-stop
    }
  }
  ringAnimFrame = requestAnimationFrame(step);
}
 
function stopRingAnimation() {
  if (ringAnimFrame) cancelAnimationFrame(ringAnimFrame);
  ringProgress.style.strokeDashoffset = RING_CIRCUM;
}
 
function setRingState(state) {
  micRing.className = `mic-ring ${state}`;
}
 
// ── Feedback ──────────────────────────────────────────────────────────────────
function showFeedback(result) {
  feedbackBox.classList.remove("hidden", "correct", "wrong");
  feedbackBox.classList.add(result.correct ? "correct" : "wrong");
  const extra = result.transcription ? ` — heard: "${result.transcription}"` : "";
  feedbackBox.textContent = result.feedback + extra;
}
 
function hideFeedback() {
  feedbackBox.classList.add("hidden");
  feedbackBox.classList.remove("correct", "wrong");
}
 
// ── Back button ───────────────────────────────────────────────────────────────
backBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  karaokeScreen.classList.remove("active");
  uploadScreen.classList.add("active");
  startBtn.textContent = "LET'S GO →";
  startBtn.disabled = false;
});

// ── Presets ───────────────────────────────────────────────────────────────────
async function loadPresets() {
  try {
    const res   = await fetch(`${API}/presets`);
    const songs = await res.json();
    presetList.innerHTML = "";
    songs.forEach(song => {
      const btn = document.createElement("button");
      btn.className = "preset-btn";
      btn.textContent = song.name;
      btn.addEventListener("click", () => selectPreset(song.id));
      presetList.appendChild(btn);
    });
  } catch (e) {
    // no presets available, hide the section silently
  }
}

async function selectPreset(id) {
  try {
    const res  = await fetch(`${API}/presets/${id}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    lyrics    = data.lyrics;
    lineIndex = 0;
    showKaraokeScreen();
  } catch (err) {
    alert("Could not load preset: " + err.message);
  }
}

loadPresets();