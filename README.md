# AI Meeting Summarizer

A Django web app that turns meeting audio or text into a summary, action items and key dates, and exports the result as a PDF.

## Features

- Upload an audio file, drag and drop one, or record live in the browser
- Paste a transcript instead of audio
- Speech to text with Whisper (`openai/whisper-small`)
- Summary with BART (`facebook/bart-large-cnn`)
- Action item and important date extraction, with context for each date
- PDF export with the summary, transcript, action items and dates

## Requirements

- Windows 10 or newer
- Python 3.12 or newer
- About 300 MB of free disk space
- Internet on the first run, to download the models

## Setup

```bash
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Usage

1. Upload or record audio, or paste text into the box.
2. Click **Process**.
3. Read the transcript, summary, action items and dates.
4. Click the blue button to export a PDF.

## Other files

- `gradio_demo.py`: a small Gradio version of the same pipeline
- `launcher.py`: starts the server for the packaged Windows build
- `LiveDemo.mp4`: screen recording of the app

## Contact

Haris Majeed Raja, bscs22017@itu.edu.pk
