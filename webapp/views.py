import logging
import os
import tempfile
from typing import List, Dict

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import MeetingForm
from core.application.orchestrator import (
    summarize_from_text,
    process_audio,
    generate_pdf_bytes,
)

logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """
    Main UI:
    - Upload audio or provide text
    - ASR + summarization + extraction
    """
    transcript = ""
    summary = ""
    actions: List[str] = []
    dates: List[Dict[str, str]] = []

    if request.method == "POST":
        form = MeetingForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data.get("text_input") or ""
            audio_file = form.cleaned_data.get("audio_file")

            try:
                if audio_file:
                    # Use default OS temp folder (fix for OneDrive)
                    tmp_suffix = os.path.splitext(audio_file.name)[1] or ".tmp"
                    with tempfile.NamedTemporaryFile(
                        suffix=tmp_suffix, delete=False
                    ) as tmp:
                        for chunk in audio_file.chunks():
                            tmp.write(chunk)
                        tmp_path = tmp.name

                    logger.info("Processing uploaded audio: %s", tmp_path)
                    transcript, summary, actions, dates = process_audio(tmp_path)

                    # Remove temp file after processing
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        logger.warning("Could not delete temp file: %s", tmp_path)

                else:
                    # Text-only mode
                    transcript = text
                    summary, actions, dates = summarize_from_text(text)

                # Save results to session for PDF download
                request.session["transcript"] = transcript
                request.session["summary"] = summary
                request.session["actions"] = actions
                request.session["dates"] = dates

            except Exception as e:
                logger.exception("Error during processing: %s", e)
                form.add_error(None, f"Error during processing: {e}")
        else:
            pass
    else:
        form = MeetingForm()

    return render(
        request,
        "webapp/index.html",
        {
            "form": form,
            "transcript": transcript,
            "summary": summary,
            "actions": actions,
            "dates": dates,
        },
    )


def export_pdf(request: HttpRequest) -> HttpResponse:
    """Generate PDF from session data"""
    transcript = request.session.get("transcript", "")
    summary = request.session.get("summary", "")
    actions = request.session.get("actions", [])
    dates = request.session.get("dates", [])

    pdf_bytes = generate_pdf_bytes(transcript, summary, actions, dates)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="meeting_summary.pdf"'
    return response


@csrf_exempt
def record_audio(request: HttpRequest) -> HttpResponse:
    """
    Endpoint for live audio recording via JS fetch() POST
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if "audio" not in request.FILES:
        return JsonResponse({"error": "No audio file provided"}, status=400)

    audio_file = request.FILES["audio"]

    try:
        # Save to system TEMP (fix)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        logger.info("Processing live-recorded audio: %s", tmp_path)
        transcript, summary, actions, dates = process_audio(tmp_path)

        try:
            os.remove(tmp_path)
        except Exception:
            logger.warning("Could not delete temp file: %s", tmp_path)

        return JsonResponse(
            {
                "transcript": transcript,
                "summary": summary,
                "actions": actions,
                "dates": dates,
            }
        )

    except Exception as e:
        logger.exception("Error during live recording processing: %s", e)
        return JsonResponse({"error": str(e)}, status=500)
