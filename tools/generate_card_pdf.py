"""Generate a one-page PDF with UzNext e-card front + back for a student."""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "murodov_behruz_e_card.pdf"
BRAND = ROOT / "assets" / "brand"

CARD = {
    "fullName": "Murodov Behruz",
    "studentId": "SA-104237",
    "cardId": "UZN-2026-0142",
    "organization": "JizPi IT PARK",
    "access": "STUDENT",
    "issueDate": "05 / 10 / 2026",
    "issueDateIso": "2026-10-05",
    "validUntilIso": "2027-10-05",
}

# Canvas size matches the Flutter card (428 x 270 logical px).
CARD_W = 428
CARD_H = 270
GREEN = (0.490, 0.761, 0.259)  # #7DC242
GREEN_DARK = (0.353, 0.627, 0.173)  # #5AA02C
LABEL = (0.541, 0.565, 0.600)  # #8A9099
VALUE = (0.894, 0.902, 0.918)  # #E4E6EA
DIVIDER = (0.290, 0.310, 0.345)  # #4A4F58


def _png(path: Path) -> ImageReader:
    return ImageReader(str(path))


def _qr_image(payload: str, size: int = 126) -> ImageReader:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=0,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _fill_gradient(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Approximate the Flutter card gradient with horizontal bands."""
    steps = 48
    for i in range(steps):
        t = i / (steps - 1)
        if t < 0.55:
            u = t / 0.55
            r = 0.200 + (0.149 - 0.200) * u  # #333436 -> #26282B
            g = 0.204 + (0.157 - 0.204) * u
            b = 0.212 + (0.169 - 0.212) * u
        else:
            u = (t - 0.55) / 0.45
            r = 0.149 + (0.106 - 0.149) * u  # #26282B -> #1B2232
            g = 0.157 + (0.133 - 0.157) * u
            b = 0.169 + (0.196 - 0.169) * u
        c.setFillColorRGB(r, g, b)
        band_h = h / steps
        c.rect(x, y + h - (i + 1) * band_h, w, band_h + 0.4, fill=1, stroke=0)


def _rounded_clip(c: canvas.Canvas, x: float, y: float, w: float, h: float, r: float) -> None:
    c.saveState()
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - 2 * r, y, x + w, y + 2 * r, -90, 90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - 2 * r, y + h - 2 * r, x + w, y + h, 0, 90)
    p.lineTo(x + r, y + h)
    p.arcTo(x, y + h - 2 * r, x + 2 * r, y + h, 90, 90)
    p.lineTo(x, y + r)
    p.arcTo(x, y, x + 2 * r, y + 2 * r, 180, 90)
    p.close()
    c.clipPath(p, stroke=0)


def _band_path(c: canvas.Canvas, x: float, y: float, w: float, h: float, far: float, near: float):
    p = c.beginPath()
    p.moveTo(x + w - far, y)
    p.lineTo(x + w, y + far)
    p.lineTo(x + w, y + near)
    p.lineTo(x + w - near, y)
    p.close()
    return p


def _stripe(c: canvas.Canvas, x: float, y: float, w: float, h: float, d: float, width: float) -> None:
    c.setStrokeColorRGB(*GREEN)
    c.setLineWidth(width)
    c.line(x + w - d - 4, y - 4, x + w + 4, y + d + 4)


def _draw_decor(c: canvas.Canvas, x: float, y: float, w: float, h: float, is_back: bool) -> None:
    c.setStrokeColorRGB(1, 1, 1)
    c.setStrokeAlpha(0.035)
    c.setLineWidth(1)
    short = min(w, h)
    cx, cy = x + w * 0.62, y + h * 0.2
    c.circle(cx, cy, short * 0.55, fill=0, stroke=1)
    c.circle(cx, cy, short * 0.9, fill=0, stroke=1)
    c.setStrokeAlpha(1)

    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.025)
    c.drawPath(_band_path(c, x, y, w, h, 200, 135), fill=1, stroke=0)
    c.setFillAlpha(1)

    if is_back:
        _stripe(c, x, y, w, h, 60, 3.5)
        _stripe(c, x, y, w, h, 30, 2.5)
    else:
        c.setFillColorRGB(*GREEN)
        c.setFillAlpha(0.14)
        c.drawPath(_band_path(c, x, y, w, h, 126, 94), fill=1, stroke=0)
        c.setFillAlpha(1)
        _stripe(c, x, y, w, h, 90, 4.5)
        _stripe(c, x, y, w, h, 56, 3)


def _field(c: canvas.Canvas, x: float, y: float, label: str, value: str, width: float = 180) -> None:
    c.setFillColorRGB(*LABEL)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y + 28, label)
    c.setFillColorRGB(*VALUE)
    c.setFont("Helvetica", 14)
    c.drawString(x, y + 10, value)
    c.setStrokeColorRGB(*DIVIDER)
    c.setLineWidth(1)
    c.line(x, y, x + width, y)


def _accent(c: canvas.Canvas, x: float, y: float, text: str, size: float = 10.5, tracking: float = 2.2) -> None:
    c.setFillColorRGB(*GREEN)
    c.rect(x, y + 3, 20, 2, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", size)
    # Simple letter-spacing approximation.
    cursor = x + 30
    for ch in text:
        c.drawString(cursor, y, ch)
        cursor += c.stringWidth(ch, "Helvetica-Bold", size) + tracking * 0.35


def _logo(c: canvas.Canvas, x: float, y: float, mark_h: float) -> None:
    mark = _png(BRAND / "uznext_mark.png")
    word = _png(BRAND / "uznext_wordmark.png")
    mark_w = mark_h  # roughly square
    word_h = mark_h * 0.5
    word_w = word_h * 4.2
    c.drawImage(mark, x, y, width=mark_w, height=mark_h, mask="auto")
    c.drawImage(
        word,
        x + mark_w + mark_h * 0.3,
        y + (mark_h - word_h) / 2,
        width=word_w,
        height=word_h,
        mask="auto",
    )


def draw_front(c: canvas.Canvas, x: float, y: float) -> None:
    w, h = CARD_W, CARD_H
    _rounded_clip(c, x, y, w, h, 18)
    _fill_gradient(c, x, y, w, h)
    _draw_decor(c, x, y, w, h, is_back=False)

    _logo(c, x + 26, y + h - 26 - 28, 28)

    c.setFont("Helvetica-Bold", 15)
    c.setFillColorRGB(1, 1, 1)
    title_x = x + w - 26 - c.stringWidth("JizPi IT PARK", "Helvetica-Bold", 15)
    c.drawString(title_x, y + h - 29 - 14, "JizPi ")
    jiz_w = c.stringWidth("JizPi ", "Helvetica-Bold", 15)
    c.setFillColorRGB(*GREEN)
    c.drawString(title_x + jiz_w, y + h - 29 - 14, "IT PARK")

    _accent(c, x + 28, y + h - 104 - 12, "STUDENT ACCESS", size=11, tracking=3.0)
    _field(c, x + 28, y + 30, "FULL NAME", CARD["fullName"], width=200)
    _field(c, x + 256, y + 30, "STUDENT ID", CARD["studentId"], width=112)
    c.restoreState()


def draw_back(c: canvas.Canvas, x: float, y: float) -> None:
    w, h = CARD_W, CARD_H
    _rounded_clip(c, x, y, w, h, 18)
    _fill_gradient(c, x, y, w, h)
    _draw_decor(c, x, y, w, h, is_back=True)

    # Top green bar
    c.setFillColorRGB(*GREEN_DARK)
    c.rect(x, y + h - 6, w / 2, 6, fill=1, stroke=0)
    c.setFillColorRGB(*GREEN)
    c.rect(x + w / 2, y + h - 6, w / 2, 6, fill=1, stroke=0)

    _logo(c, x + w - 26 - 110, y + h - 24 - 24, 24)

    # QR must match the opaque backend payload (UZN.<token>), never PII JSON.
    # Example: QR_PAYLOAD=UZN.xxxxx python tools/generate_card_pdf.py
    qr_payload = os.environ.get("QR_PAYLOAD", "").strip()
    if not qr_payload:
        print(
            "Set QR_PAYLOAD to the student's opaque token from GET /card/me "
            "(e.g. UZN.xxxxx). Refusing to embed PII in the QR.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    plate = 146
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x + 24, y + h - 58 - plate, plate, plate, 12, fill=1, stroke=0)
    qr = _qr_image(qr_payload, 126)
    c.drawImage(qr, x + 24 + 10, y + h - 58 - plate + 10, width=126, height=126, mask="auto")

    _accent(c, x + 26, y + h - 220 - 10, "SCAN TO ACCESS", size=9.5, tracking=2.4)
    _field(c, x + 200, y + h - 82 - 40, "CARD ID", CARD["cardId"], width=170)
    _field(c, x + 200, y + h - 144 - 40, "ISSUE DATE", CARD["issueDate"], width=170)
    c.restoreState()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(OUT), pagesize=A4)

    # Soft page background
    c.setFillColorRGB(0.94, 0.95, 0.96)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColorRGB(0.15, 0.16, 0.18)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_w / 2, page_h - 22 * mm, "UzNext E-Card")
    c.setFillColorRGB(0.35, 0.38, 0.42)
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_w / 2, page_h - 28 * mm, CARD["fullName"])

    scale = min((page_w - 40 * mm) / CARD_W, 1.15)
    draw_w = CARD_W * scale
    draw_h = CARD_H * scale
    left = (page_w - draw_w) / 2

    # Front
    c.setFillColorRGB(0.45, 0.48, 0.52)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, page_h - 38 * mm, "FRONT")
    c.saveState()
    c.translate(left, page_h - 38 * mm - 6 - draw_h)
    c.scale(scale, scale)
    # Drop shadow
    c.setFillColorRGB(0, 0, 0)
    c.setFillAlpha(0.12)
    c.roundRect(4, -6, CARD_W, CARD_H, 18, fill=1, stroke=0)
    c.setFillAlpha(1)
    draw_front(c, 0, 0)
    c.restoreState()

    # Back
    back_top = page_h - 38 * mm - 6 - draw_h - 14 * mm
    c.setFillColorRGB(0.45, 0.48, 0.52)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, back_top, "BACK")
    c.saveState()
    c.translate(left, back_top - 6 - draw_h)
    c.scale(scale, scale)
    c.setFillColorRGB(0, 0, 0)
    c.setFillAlpha(0.12)
    c.roundRect(4, -6, CARD_W, CARD_H, 18, fill=1, stroke=0)
    c.setFillAlpha(1)
    draw_back(c, 0, 0)
    c.restoreState()

    c.setFillColorRGB(0.55, 0.58, 0.62)
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        page_w / 2,
        14 * mm,
        f"{CARD['cardId']}  ·  {CARD['organization']}  ·  Valid until {CARD['validUntilIso']}",
    )

    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
