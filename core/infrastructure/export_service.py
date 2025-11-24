import io
from typing import List, Dict, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_meeting_to_pdf(
    transcript: Optional[str],
    summary: str,
    actions: List[str],
    dates: List[Dict[str, str]],
) -> bytes:
    """
    Generate a PDF containing transcript, summary, action items, and important dates.
    Returns the PDF as bytes (for Django HttpResponse).
    """
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def write_text_block(title: str, text_lines: List[str], y_start: float) -> float:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_start, title)
        y = y_start - 20
        pdf.setFont("Helvetica", 10)
        for line in text_lines:
            if y < 50:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)
            pdf.drawString(60, y, line)
            y -= 14
        return y - 10

    y = height - 50

    # Summary
    summary_lines = summary.splitlines() or [summary]
    y = write_text_block("Summary:", summary_lines, y)

    # Transcript (optional)
    if transcript:
        transcript_lines = transcript.splitlines()
        y = write_text_block("Transcript:", transcript_lines, y)

    # Actions
    if actions:
        action_lines = ["- " + a for a in actions]
    else:
        action_lines = ["(No action items found.)"]
    y = write_text_block("Action Items:", action_lines, y)

    # Dates
    if dates:
        date_lines = ["- %s: %s" % (d["date"], d["context"]) for d in dates]
    else:
        date_lines = ["(No important dates found.)"]
    write_text_block("Important Dates:", date_lines, y)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getbytes() if hasattr(buffer, "getbytes") else buffer.getvalue()
