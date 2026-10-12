# The Lenny Growth Assistant - Demo Video Walkthrough Guide
**Deliverable:** 2-3 Minute Walkthrough Video Script & Demonstration Plan  
**Target Audience:** Forward Deployed Engineering Hiring Team & Client Evaluators  

---

## 1. Before Recording
- Keep the final video between 2 and 3 minutes, with your camera visible throughout.
- Start Ollama and run `ollama pull llama3.2` if the model is not installed.
- Confirm `/api/models/status` reports Ollama as available before recording. Do not claim a local-model response if the app is using its fallback.
- Restart old app processes before `python run.py` so the recording uses the current code. If the ports are already occupied, stop the old frontend/backend first.
- Have the Elena Verna question ready, and warm up the model with one request so the recording is not spent waiting for its first response.
- Close personal tabs and keep `.env` files, API keys, and private information off screen.

---

## 2. Word-for-Word Video Script

### [0:00 - 0:25] The Problem
> **(Camera visible; show the app beside your webcam.)**
>
> "Hi, I'm [name]. Product and growth teams have useful operator advice spread across long podcast transcripts. Finding the relevant passage, checking where it came from, and turning it into something reusable takes time. I built the Lenny Growth Assistant to make that workflow quicker: ask a question, inspect the transcript excerpt, and create an artifact in the same app."

---

### [0:25 - 1:05] Ask and Verify
> **(Show the chat and submit the question.)**
>
> "I'll ask: 'What did Elena Verna say about product-market fit?' The local index searches 50 transcript files using BM25 keyword retrieval. Here are the source cards. I'll open one to inspect its timestamp and excerpt. In this interview, Verna contrasts product-market fit evolving over years with the faster pace in AI, where teams may need to recapture it every few months. The citation lets us check the source instead of taking a generated answer on trust."

---

### [1:05 - 1:30] Local Model
> **(Show the provider selector and Ollama-ready status.)**
>
> "The demo is using Ollama with `llama3.2`, running locally. The provider selector makes the active engine visible. Local inference avoids sending this prompt to a cloud provider, though response speed and quality depend on the machine and model. If the Ollama status is unavailable, this app falls back to transcript excerpts; that fallback is not model-generated analysis."

---

### [1:30 - 2:05] Follow-up and Artifact
> **(Ask a follow-up, then open the Ship 30 prompt or an HTML artifact.)**
>
> "I'll ask a follow-up in the same chat to show that recent turns are carried into the next request. The Ship 30 prompt can draft a longer essay when a model is available. The Artifact Viewer renders Markdown beside the conversation. HTML previews run inside a sandboxed iframe; Markdown is sanitized before display. With Ollama off, essay requests produce a short source brief, so I'm showing the model-backed version here."

---

### [2:05 - 2:35] Trade-off and Close
> **(Camera visible; briefly return to the app or README.)**
>
> "One trade-off is lexical BM25 retrieval. It's lightweight, local, and straightforward to inspect, but it can miss a relevant passage when someone asks with different wording. A semantic index would help with paraphrases, at the cost of more dependencies and setup. For local development, sessions use SQLite; Docker Compose also defines a PostgreSQL path. The README covers setup and tests. Thanks for watching."

---

## 3. Recording on Windows
1. Install OBS Studio and create a scene with **Display Capture**, **Video Capture Device** (webcam), and **Audio Input Capture** (microphone).
2. Resize the webcam feed to a small corner overlay, but keep your face visible for the full recording. Check mic levels and make a short test recording.
3. Record the browser at 1080p if available. Keep the cursor deliberate, speak at a steady pace, and aim for about 2:30.
4. Review the video once for readable text, clear audio, correct Ollama status, and accidental secrets before uploading.

## 4. Upload
Upload the finished recording to YouTube as **Unlisted** or **Public**, then paste its share URL into the submission form. Do not use Private visibility if evaluators need to open the link.
