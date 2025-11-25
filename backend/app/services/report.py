from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
import json
import uuid


class ReportService:
    """
    Generates a simple PDF report for a PO–Invoice match result.
    """

    def __init__(self, output_dir: str = "./uploads/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------
    # Generate PDF report
    # -------------------------------------------------------
    def generate_match_report(self, match_id: int, po: dict, inv: dict, result: dict) -> str:
        """
        Creates a PDF summarizing:
        - PO details
        - Invoice details
        - mismatches
        - fraud flags
        - confidence score

        Returns: file path to the PDF report.
        """

        filename = f"report_{match_id}_{uuid.uuid4().hex}.pdf"
        file_path = self.output_dir / filename

        # Create PDF
        c = canvas.Canvas(str(file_path), pagesize=A4)
        width, height = A4
        y = height - 50

        # -------------------------------------------------------
        # Title
        # -------------------------------------------------------
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "Invoice Matching Report")
        y -= 40

        c.setFont("Helvetica", 12)

        # -------------------------------------------------------
        # Basic info
        # -------------------------------------------------------
        c.drawString(50, y, f"Match ID: {match_id}")
        y -= 20

        c.drawString(50, y, f"Confidence Score: {result.get('score')}")
        y -= 20

        # -------------------------------------------------------
        # PO Summary
        # -------------------------------------------------------
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Purchase Order Summary")
        y -= 25

        c.setFont("Helvetica", 12)
        for key in ["doc_number", "date", "vendor_name", "grand_total"]:
            c.drawString(60, y, f"{key}: {po.get(key)}")
            y -= 18

        y -= 10

        # -------------------------------------------------------
        # Invoice Summary
        # -------------------------------------------------------
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Invoice Summary")
        y -= 25

        c.setFont("Helvetica", 12)
        for key in ["doc_number", "date", "vendor_name", "grand_total"]:
            c.drawString(60, y, f"{key}: {inv.get(key)}")
            y -= 18

        y -= 10

        # -------------------------------------------------------
        # Mismatches
        # -------------------------------------------------------
        mismatches = result.get("mismatches", [])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Mismatches")
        y -= 25
        c.setFont("Helvetica", 12)

        if not mismatches:
            c.drawString(60, y, "None")
            y -= 20
        else:
            for m in mismatches:
                text = json.dumps(m)
                c.drawString(60, y, text[:100])
                y -= 18
                if y < 100:
                    c.showPage()
                    y = height - 80

        y -= 10

        # -------------------------------------------------------
        # Fraud Flags
        # -------------------------------------------------------
        fraud_flags = result.get("fraud_flags", [])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Fraud Flags")
        y -= 25
        c.setFont("Helvetica", 12)

        if not fraud_flags:
            c.drawString(60, y, "None")
            y -= 20
        else:
            for flag in fraud_flags:
                c.drawString(60, y, f"- {flag}")
                y -= 18
                if y < 100:
                    c.showPage()
                    y = height - 80

        # Save PDF
        c.save()

        return str(file_path)
