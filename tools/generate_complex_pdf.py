from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from pathlib import Path

out = Path("data/complex_sample_dates.pdf")
out.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(out), pagesize=letter)
width, height = letter

# Header
c.setFont("Helvetica-Bold", 14)
c.drawString(72, height - 50, "Acme Pharmaceuticals — Certificate of Analysis")
c.setFont("Helvetica", 9)
c.drawRightString(width - 72, height - 50, "Document ID: APO-2025-001")

# Intro paragraph
text = c.beginText(72, height - 90)
text.setFont("Times-Roman", 11)
intro = (
    "This report documents the analysis performed on batch #A123. The material was sampled and analyzed "
    "on multiple dates. The primary manufacturing date for the batch is recorded as 2025-01-15. Further testing "
    "was performed on January 20, 2025 and confirmed on 20/01/2025 in secondary logs."
)
for line in intro.split('. '):
    text.textLine(line.strip() + '.')
c.drawText(text)

# Paragraph with embedded dates and ambiguity
text2 = c.beginText(72, height - 170)
text2.setFont("Times-Roman", 11)
para2 = (
    "Note: The shipment arrived on 02/03/25 which is recorded in the shipping manifest. In some records the "
    "date appears as 03-02-2025; please confirm local vs international date formats. A handwritten note on the "
    "packing slip reads 'Received 5th Feb 2025' which should be treated as 2025-02-05 unless otherwise corrected."
)
for ln in para2.split('. '):
    text2.textLine(ln.strip() + '.')
c.drawText(text2)

# Bulleted list of key dates
bul_y = height - 260
c.setFont("Helvetica-Bold", 12)
c.drawString(72, bul_y, "Key Dates:")
bul_y -= 18
c.setFont("Helvetica", 11)
bullets = [
    "Mfg Date: 01/15/2025",
    "Test Date: 15.01.25",
    "Expiry: 2025-07-15",
    "QC Approval: March 10, 2025",
]
for b in bullets:
    c.drawString(84, bul_y, f"• {b}")
    bul_y -= 16

# Draw a simple table with headers and date cells
table_x = 72
table_y = bul_y - 20
row_height = 18
col_widths = [200, 150, 120]
headers = ["Location/Field", "Date Found", "Notes"]
rows = [
    ("Table Row 1: Mfg Date", "01/15/2025", "Located under header 'Mfg Date'"),
    ("Table Row 2: Received", "2025-01-05", "Scanned handwritten annotation"),
    ("Table Row 3: Shipped", "02/03/25", "Ambiguous format"),
]
# header
c.setFillColor(colors.lightgrey)
c.rect(table_x, table_y - row_height, sum(col_widths), row_height, fill=True, stroke=False)
c.setFillColor(colors.black)
for i, h in enumerate(headers):
    c.drawString(table_x + sum(col_widths[:i]) + 6, table_y - row_height + 4, h)
# rows
for r_idx, row in enumerate(rows):
    y = table_y - row_height * (r_idx + 2)
    for c_idx, cell in enumerate(row):
        x = table_x + sum(col_widths[:c_idx]) + 6
        c.drawString(x, y + 4, str(cell))
    # row lines
    c.line(table_x, y, table_x + sum(col_widths), y)
# vertical lines
x = table_x
for w in col_widths:
    c.line(x, table_y, x, table_y - row_height * (len(rows) + 1))
    x += w

# Footer
c.setFont("Helvetica-Oblique", 9)
c.drawString(72, 36, "Prepared by QA Department — Reviewed: 2025-03-15")
c.drawRightString(width - 72, 36, "Page 1 of 2")

c.showPage()

# Page 2: more narrative and a boxed annotation
c.setFont("Helvetica-Bold", 13)
c.drawString(72, height - 50, "Supplementary Notes and Observations")

ptext = c.beginText(72, height - 90)
ptext.setFont("Times-Roman", 11)
longpara = (
    "The following supplementary observations were noted during laboratory review. Several instruments reported "
    "timestamps in UTC; one instrument logged 2025-03-10T14:23:00Z which corresponds to local date 2025-03-10. "
    "Cross-referencing with the manifest (dated 10-Mar-2025) confirms the timeline. An internal audit flagged an "
    "inconsistency where a form shows 01/02/2025 which likely refers to Feb 1st, 2025 in the source country."
)
for ln in longpara.split('. '):
    ptext.textLine(ln.strip() + '.')
c.drawText(ptext)

# Draw boxed handwritten-like note
note_x = 72
note_y = height - 260
c.setStrokeColor(colors.darkgray)
c.rect(note_x, note_y - 60, 400, 50, fill=False)
c.setFont("Times-Italic", 11)
c.drawString(note_x + 8, note_y - 30, "Handwritten: Approve if within spec — signed: J. Doe 5th Feb 2025")

# Footer page 2
c.setFont("Helvetica-Oblique", 9)
c.drawString(72, 36, "Confidential — Internal Use Only")
c.drawRightString(width - 72, 36, "Page 2 of 2")

c.showPage()
c.save()

print(f"Complex sample PDF written to: {out}")
