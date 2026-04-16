from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

out = Path("data/sample_dates.pdf")
out.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(out), pagesize=letter)
width, height = letter
c.setFont("Helvetica", 12)

lines = [
    "Certificate of Analysis",
    "",
    "Manufacturing Date: 01/15/2025",
    "Expiry Date: 15-Jan-2025",
    "Received Date: January 5, 2025",
    "Test Date: 15.01.25",
    "Shipped On: 02/03/25",
    "Handwritten style example: 5th Feb 2025",
    "Another format: 2025-03-10",
    "Ambiguous: 01/02/2025",
    "End of sample document.",
]

y = height - 72
for ln in lines:
    c.drawString(72, y, ln)
    y -= 18

c.showPage()
c.save()

print(f"Sample PDF written to: {out}")
