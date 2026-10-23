from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

PRIMARY = "#1e1b4b"     # same indigo / saffron as the web app
ACCENT = "#f97316"

# The built-in PDF fonts have no Rupee glyph. Use DejaVu when the system has it,
# otherwise fall back to "Rs." so the PDF never shows a black box.
_FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
    ("/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"),
]


def _register_unicode_font():
    for regular, bold in _FONT_CANDIDATES:
        if Path(regular).exists() and Path(bold).exists():
            try:
                pdfmetrics.registerFont(TTFont("TM-Regular", regular))
                pdfmetrics.registerFont(TTFont("TM-Bold", bold))
                pdfmetrics.registerFontFamily("TM-Regular", normal="TM-Regular", bold="TM-Bold",
                                              italic="TM-Regular", boldItalic="TM-Bold")
                return "TM-Regular", "TM-Bold", "\u20b9"
            except Exception:  # noqa: BLE001
                continue
    return "Helvetica", "Helvetica-Bold", "Rs. "


def _fmt_money(value, symbol: str) -> str:
    try:
        n = int(round(float(value or 0)))
    except (TypeError, ValueError):
        n = 0
    s = f"{n:,}"                                   # Indian grouping: 1,23,456
    if n >= 1000:
        head, tail = s.replace(",", "")[:-3], s.replace(",", "")[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return f"{symbol}{s}"


def _p(text) -> str:
    return escape(str(text if text is not None else ""))


def build_trip_pdf(trip, itinerary: dict) -> BytesIO:
    font, font_bold, rupee = _register_unicode_font()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                            title=f"TravelMate AI - {trip.destination}", author="TravelMate AI")
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName=font_bold, fontSize=20, textColor=PRIMARY)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=font_bold, fontSize=13,
                        textColor=ACCENT, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName=font, fontSize=10, leading=14)
    small = ParagraphStyle("small", parent=body, fontSize=9, textColor="#64748b")

    dates = f"{trip.start_date or 'flexible'} to {trip.end_date or 'flexible'}"
    story = [
        Paragraph(_p(f"TravelMate AI - {trip.destination}"), h1),
        Paragraph(_p(dates), body),
        Paragraph(_p(f"Travellers: {trip.travelers}  |  Budget: {_fmt_money(trip.budget, rupee)}"), body),
        Spacer(1, 10),
    ]

    grand_total = 0.0
    gt = itinerary.get("getting_there")
    if gt and gt.get("cost_inr"):
        grand_total += float(gt["cost_inr"])
        story.append(Paragraph(_p(
            f"Getting there: {gt.get('from_place') or 'Home'} to {gt.get('to', '')} by {gt.get('mode', '')} "
            f"(round trip, ~{gt.get('distance_km', 0)} km): {_fmt_money(gt['cost_inr'], rupee)}"), body))
        story.append(Spacer(1, 8))

    for day in itinerary.get("days", []) or []:
        day_total = sum(float(a.get("estimated_cost_inr", a.get("estimated_cost", 0)) or 0)
                        + float((a.get("travel") or {}).get("cost_inr", 0) or 0)
                        for a in day.get("activities", []) or [])
        grand_total += day_total
        head = f"Day {day.get('day_number', '')} - {day.get('theme', '')}"
        if day.get("date"):
            head += f"  ({day['date']})"
        story.append(Paragraph(_p(head), h2))
        for a in day.get("activities", []) or []:
            cost = a.get("estimated_cost_inr", a.get("estimated_cost", 0))
            tr = a.get("travel") or {}
            if tr.get("mode") and (tr.get("distance_km") or tr.get("cost_inr")):
                story.append(Paragraph(_p(
                    f"  > {tr['mode']}, {tr.get('distance_km', 0)} km, ~{tr.get('duration_minutes', 0)} min, "
                    f"{_fmt_money(tr.get('cost_inr', 0), rupee)}"), small))
            line = (f"<b>{_p(a.get('start_time', ''))}  {_p(a.get('name', ''))}</b><br/>"
                    f"{_p(a.get('description', ''))}<br/>"
                    f"<font color='#64748b'>Est. cost: {_p(_fmt_money(cost, rupee))}"
                    f"{' | ' + _p(a.get('location')) if a.get('location') else ''}</font>")
            story.append(Paragraph(line, body))
            story.append(Spacer(1, 5))
        story.append(Paragraph(_p(f"Day total: {_fmt_money(day_total, rupee)}"), small))
        story.append(Spacer(1, 8))

    story.append(Paragraph(_p(f"Estimated total: {_fmt_money(grand_total, rupee)}"), h2))

    notes = (itinerary.get("assumptions") or []) + (itinerary.get("warnings") or [])
    if notes:
        story.append(PageBreak())
        story.append(Paragraph("Assumptions & warnings", h2))
        for n in notes:
            story.append(Paragraph(_p(f"\u2022 {n}"), body))

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor("#94a3b8")
        canvas.drawString(18 * mm, 10 * mm, "Generated by TravelMate AI - estimates only, verify prices before booking")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {_doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buf.seek(0)
    return buf
