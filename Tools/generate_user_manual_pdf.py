import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

os.makedirs("docs", exist_ok=True)

pdf_path = "docs/AccuSense_User_Manual.pdf"

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    rightMargin=16 * mm,
    leftMargin=16 * mm,
    topMargin=14 * mm,
    bottomMargin=14 * mm,
)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontSize=18,
    textColor=colors.HexColor("#0B4F9C"),
    spaceAfter=12,
)

heading = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=12,
    textColor=colors.HexColor("#0B4F9C"),
    spaceBefore=10,
    spaceAfter=6,
)

body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=9,
    leading=12,
    spaceAfter=5,
)

elements = []

elements.append(Paragraph("AccuSense Quotation System User Guide", title))

sections = [
    ("1. Login", "Open the app, enter your email address and password, then click Login."),
    ("2. Creating a New Quote", "Complete Customer Name, Company, Site and Salesperson details. Add products using Load Solution Template or Add Products Manually."),
    ("3. Loading Solution Templates", "Expand Load Solution Template, select the required template and click Load Template Into Quote."),
    ("4. Adding Products Manually", "Expand Add Products Manually, select category, product, quantity and discount if applicable, then click Add To Quote."),
    ("5. Quote Summary", "The Quote Summary displays all items. Quantities, discounts and pricing can be reviewed before generating the quote."),
    ("6. Annual Monitoring Fee", "When sensor products are included, the system automatically adds the Annual Monitoring Fee based on the Monitoring Fee product in the Products sheet. In summarized quotes it appears under the configured Identification, for example Service - Monitoring."),
    ("7. Quote Output Type", "Summarized Quote is the default. It groups products by Identification. Detailed Quote shows individual product lines."),
    ("8. Generating a Quote PDF", "Select the output type and click Generate / Save PDF. The PDF includes customer details, salesperson details, quote table, totals, terms and conditions, and salesperson signature if configured."),
    ("9. PDF Layout Notes", "The Billing and Discount columns are hidden on PDF quotations, but remain available inside the quotation editor."),
    ("10. Salesperson Signatures", "A signature can be linked in the Users sheet using the Signature File column, for example signatures/eddie_signature.png."),
    ("11. Loading Existing Quotes", "Use Load Existing Quote in the sidebar. Loading an existing quote does not automatically create a revision. The original quote number is retained."),
    ("12. Download Existing PDF", "After loading an existing quote, use Download Existing PDF to download the original PDF without changing the quote number."),
    ("13. Create Revision", "Use Create Revision only when changes are required. Example: Q-20260601-10, Q-20260601-10-R01, Q-20260601-10-R02."),
    ("14. Approval Workflow", "If a quote exceeds the user's approval limit, it is submitted for approval before it can be issued."),
    ("15. Approvals Page", "Authorised approvers can review, approve or reject quotes and add notes."),
    ("16. My Pending Quotes", "Users can view pending, approved and rejected quotes together with approval comments."),
    ("17. Sales Report", "Users with permission can access the Sales Report. Access is controlled through the Users sheet."),
    ("18. Troubleshooting", "Check Products sheet if products are missing. Customer Name, Company and Salesperson are required. If an existing PDF is missing, regenerate it if required."),
    ("19. Support", "For support, configuration changes or user access requests, contact the AccuSense system administrator."),
]

for h, text in sections:
    elements.append(Paragraph(h, heading))
    elements.append(Paragraph(text, body))
    elements.append(Spacer(1, 4))

doc.build(elements)

print(f"PDF manual created: {pdf_path}")