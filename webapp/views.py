import logging
import os
import tempfile
from typing import List, Dict

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
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
    - Captures text transcript and/or audio file.
    - Invokes orchestrator to run ASR / summarisation / extraction.
    - Renders results.
    """
    transcript = ""
    summary = ""
    actions = []  # type: List[str]
    dates = []    # type: List[Dict[str, str]]

    if request.method == "POST":
        form = MeetingForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data.get("text_input") or ""
            audio_file = form.cleaned_data.get("audio_file")

            try:
                if audio_file:
                    # Save uploaded audio to a temporary file
                    with tempfile.NamedTemporaryFile(
                        suffix=os.path.splitext(audio_file.name)[1],
                        dir=str(settings.MEDIA_ROOT),
                        delete=False,
                    ) as tmp:
                        for chunk in audio_file.chunks():
                            tmp.write(chunk)
                        tmp_path = tmp.name

                    logger.info("Processing uploaded audio: %s", tmp_path)
                    transcript, summary, actions, dates = process_audio(tmp_path)

                    # Optionally remove temp file
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        logger.warning("Could not delete temp file: %s", tmp_path)
                else:
                    # Text-only flow
                    transcript = text
                    summary, actions, dates = summarize_from_text(text)

                # Store results in session for PDF export
                request.session["transcript"] = transcript
                request.session["summary"] = summary
                request.session["actions"] = actions
                request.session["dates"] = dates

            except Exception as e:
                logger.exception("Error during processing: %s", e)
                form.add_error(None, f"Error during processing: {e}")
        else:
            # form invalid; errors will be shown
            pass
    else:
        form = MeetingForm()

    context = {
        "form": form,
        "transcript": transcript,
        "summary": summary,
        "actions": actions,
        "dates": dates,
    }
    return render(request, "webapp/index.html", context)


def export_pdf(request: HttpRequest) -> HttpResponse:
    """
    Export adapter: generate a PDF containing summary, transcript, actions, dates.
    """
    transcript = request.session.get("transcript", "")
    summary = request.session.get("summary", "")
    actions = request.session.get("actions", [])
    dates = request.session.get("dates", [])

    pdf_bytes = generate_pdf_bytes(transcript, summary, actions, dates)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="meeting_summary.pdf"'
    return response


@csrf_exempt  # For demo only; in production you'd handle CSRF properly
def record_audio(request: HttpRequest) -> HttpResponse:
    """
    Live audio recording endpoint.

    Front-end JS sends a recorded audio blob via POST (multipart/form-data).
    This view:
    - saves the blob to a temp file,
    - runs ASR + summarisation + extraction through orchestrator,
    - returns JSON with transcript, summary, actions, dates.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if "audio" not in request.FILES:
        return JsonResponse({"error": "No audio file provided"}, status=400)

    audio_file = request.FILES["audio"]

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".webm", dir=str(settings.MEDIA_ROOT), delete=False
        ) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        logger.info("Processing live-recorded audio: %s", tmp_path)
        transcript, summary, actions, dates = process_audio(tmp_path)

        try:
            os.remove(tmp_path)
        except OSError:
            logger.warning("Could not delete temp file: %s", tmp_path)

        # Do NOT write these into session here; JS will handle UI
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
