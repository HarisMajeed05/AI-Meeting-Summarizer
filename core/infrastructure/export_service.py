import io
from typing import List, Dict, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def export_meeting_to_pdf(
    transcript: Optional[str],
    summary: str,
    actions: List[str],
    dates: List[Dict[str, str]],
) -> bytes:

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    LEFT = 20 * mm
    RIGHT = width - 20 * mm
    TOP = height - 20 * mm
    BOTTOM = 20 * mm
    LINE_HEIGHT = 14
    WRAP_WIDTH = RIGHT - LEFT

    pdf.setFont("Helvetica", 10)

    # ---------- WORD WRAP FUNCTION ----------
    def wrap_text(text: str, font="Helvetica", size=10):
        """
        Wrap text into lines that fit within WRAP_WIDTH.
        """
        pdf.setFont(font, size)
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if pdf.stringWidth(test_line, font, size) < WRAP_WIDTH:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    # ---------- BLOCK WRITER (handles page breaks + wrapping) ----------
    def write_block(title: str, text: str, y: float):
        nonlocal pdf

        # Heading
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(LEFT, y, title)
        y -= 18

        pdf.setFont("Helvetica", 10)

        # Split into paragraphs
        paragraphs = text.split("\n")

        for para in paragraphs:
            if not para.strip():
                y -= LINE_HEIGHT
                continue

            wrapped_lines = wrap_text(para)

            for line in wrapped_lines:
                if y < BOTTOM:
                    pdf.showPage()
                    y = TOP
                    pdf.setFont("Helvetica", 10)
                pdf.drawString(LEFT + 10, y, line)
                y -= LINE_HEIGHT

        y -= LINE_HEIGHT
        return y

    # START AT TOP
    y = TOP

    # ---------- SUMMARY ----------
    y = write_block("Summary:", summary, y)

    # ---------- TRANSCRIPT ----------
    if transcript:
        y = write_block("Transcript:", transcript, y)

    # ---------- ACTION ITEMS ----------
    actions_text = "\n".join([f"- {a}" for a in actions]) if actions else "(No action items found.)"
    y = write_block("Action Items:", actions_text, y)

    # ---------- IMPORTANT DATES ----------
    if dates:
        date_text = "\n".join([f"- {d['date']}: {d['context']}" for d in dates])
    else:
        date_text = "(No important dates found.)"
    y = write_block("Important Dates:", date_text, y)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
