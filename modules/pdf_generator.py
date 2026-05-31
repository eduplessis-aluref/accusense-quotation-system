import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =====================================================
# COLORS
# =====================================================

BLUE = colors.HexColor("#0B4F9C")
GREEN = colors.HexColor("#6CB33F")
LIGHT_BLUE = colors.HexColor("#F2F6FB")


# =====================================================
# FONTS
# =====================================================

FONT_NORMAL = "Calibri"
FONT_BOLD = "Calibri-Bold"

try:
    pdfmetrics.registerFont(TTFont(FONT_NORMAL, "calibri.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, "calibrib.ttf"))
except Exception:
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


# =====================================================
# HELPERS
# =====================================================

def first_name_only(name):
    if not str(name).strip():
        return "Customer"

    return str(name).strip().split()[0]


def image_aspect(path, width_mm):

    img = ImageReader(path)
    iw, ih = img.getSize()

    width = width_mm * mm
    height = width * ih / iw

    return Image(
        path,
        width=width,
        height=height
    )


# =====================================================
# FOOTER DRAWING
# =====================================================

def draw_footer(canvas_obj, doc):

    page_width, page_height = A4

    canvas_obj.saveState()

    # =================================================
    # BLUE WAVE
    # =================================================

    blue_path = canvas_obj.beginPath()

    blue_path.moveTo(0, 0)
    blue_path.lineTo(0, 24 * mm)

    blue_path.curveTo(
        35 * mm,
        32 * mm,
        72 * mm,
        18 * mm,
        112 * mm,
        15 * mm
    )

    blue_path.curveTo(
        150 * mm,
        12 * mm,
        180 * mm,
        22 * mm,
        page_width,
        34 * mm
    )

    blue_path.lineTo(page_width, 0)
    blue_path.close()

    canvas_obj.setFillColor(BLUE)
    canvas_obj.drawPath(
        blue_path,
        fill=1,
        stroke=0
    )

    # =================================================
    # GREEN WAVE
    # =================================================

    green_path = canvas_obj.beginPath()

    green_path.moveTo(65 * mm, 0)

    green_path.curveTo(
        105 * mm,
        22 * mm,
        145 * mm,
        7 * mm,
        178 * mm,
        9 * mm
    )

    green_path.curveTo(
        194 * mm,
        10 * mm,
        205 * mm,
        20 * mm,
        page_width,
        24 * mm
    )

    green_path.lineTo(page_width, 0)
    green_path.close()

    canvas_obj.setFillColor(GREEN)

    canvas_obj.drawPath(
        green_path,
        fill=1,
        stroke=0
    )

    # =================================================
    # FOOTER TEXT
    # =================================================

    footer_lines = [
        "70 Ceramic Curve - Alton Richards Bay. P.O. Box 102183 - Meerensee - 3901 - Kwa-Zulu Natal - South Africa",
        "Office:+27(0) 35 751 1229 Fax: +27(0) 35 751 2016 Email: info@aluref.net",
        "Reg. No. 2010/023755/07",
        "Directors: DGM Blackmore, AF Wolhüter, S Jughdis, S Jughdis (Mrs)",
    ]

    canvas_obj.setFillColor(colors.white)

    canvas_obj.setFont(
        FONT_NORMAL,
        4.8
    )

    text_x = 7 * mm
    y = 16 * mm

    for line in footer_lines:

        canvas_obj.drawString(
            text_x,
            y,
            line
        )

        y -= 2.7 * mm

    # =================================================
    # EMBLEM
    # =================================================

    emblem_path = "Emblem.png"

    if os.path.exists(emblem_path):

        try:

            img = ImageReader(emblem_path)
            iw, ih = img.getSize()

            target_width = 22 * mm
            target_height = target_width * ih / iw

            canvas_obj.saveState()
            canvas_obj.setFillAlpha(0.15)

            canvas_obj.drawImage(
                emblem_path,
                page_width - 26 * mm,
                1 * mm,
                width=target_width,
                height=target_height,
                mask="auto"
            )

            canvas_obj.restoreState()

        except Exception:
            pass

    canvas_obj.restoreState()


# =====================================================
# PDF GENERATOR
# =====================================================

def generate_pdf(
    quote_number,
    customer,
    company,
    site,
    customer_email,
    salesperson,
    salesperson_phone,
    salesperson_email,
    quote_df,
    subtotal,
    vat,
    total,
    terms,
    signature_file=""
):

    os.makedirs(
        "output/PDFs",
        exist_ok=True
    )

    pdf_path = f"output/PDFs/{quote_number}.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=13 * mm,
        leftMargin=13 * mm,
        topMargin=10 * mm,
        bottomMargin=42 * mm
    )

    styles = getSampleStyleSheet()

    # =================================================
    # STYLES
    # =================================================

    normal = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        fontName=FONT_NORMAL
    )

    bold = ParagraphStyle(
        "Bold",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        fontName=FONT_BOLD
    )

    intro_style = ParagraphStyle(
        "Intro",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        fontName=FONT_NORMAL
    )

    blue_heading = ParagraphStyle(
        "BlueHeading",
        parent=styles["Heading2"],
        fontSize=10,
        leading=12,
        textColor=BLUE,
        fontName=FONT_BOLD
    )

    quote_number_style = ParagraphStyle(
        "QuoteNumber",
        parent=styles["BodyText"],
        fontSize=10,
        leading=12,
        alignment=2,
        fontName=FONT_BOLD
    )

    elements = []

    # =================================================
    # LOGO + QUOTE NUMBER
    # =================================================

    logo_path = "Logo.png"

    if os.path.exists(logo_path):

        try:
            logo = image_aspect(
                logo_path,
                82
            )

        except Exception:
            logo = Paragraph(
                "<b>AccuSense</b>",
                styles["Heading1"]
            )

    else:

        logo = Paragraph(
            "<b>AccuSense</b>",
            styles["Heading1"]
        )

    quote_number_text = Paragraph(
        f"<font color='#0B4F9C'><b>Quotation:</b></font> "
        f"<b>{quote_number}</b>",
        quote_number_style
    )

    header_table = Table(
        [[logo, quote_number_text]],
        colWidths=[112 * mm, 70 * mm]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (0, 0), "TOP"),
        ("VALIGN", (1, 0), (1, 0), "BOTTOM"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (1, 0), (1, 0), 70),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 40))

    # =================================================
    # CUSTOMER DETAILS
    # =================================================

    details_data = [

        [
            Paragraph(
                "<font color='#0B4F9C'><b>Customer:</b></font>",
                bold
            ),

            Paragraph(customer, normal),

            "",

            Paragraph(
                "<font color='#0B4F9C'><b>Salesperson:</b></font>",
                bold
            ),

            Paragraph(salesperson, normal),
        ],

        [
            Paragraph(
                "<font color='#0B4F9C'><b>Company:</b></font>",
                bold
            ),

            Paragraph(company, normal),

            "",

            Paragraph(
                "<font color='#0B4F9C'><b>Phone:</b></font>",
                bold
            ),

            Paragraph(salesperson_phone, normal),
        ],

        [
            Paragraph(
                "<font color='#0B4F9C'><b>Site:</b></font>",
                bold
            ),

            Paragraph(site, normal),

            "",

            Paragraph(
                "<font color='#0B4F9C'><b>Email:</b></font>",
                bold
            ),

            Paragraph(salesperson_email, normal),
        ],
    ]

    details_table = Table(
        details_data,
        colWidths=[
            24 * mm,
            58 * mm,
            16 * mm,
            28 * mm,
            56 * mm
        ]
    )

    details_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 14))

    # =================================================
    # INTRO
    # =================================================

    elements.append(
        Paragraph(
            f"Dear {first_name_only(customer)}, thank you for the opportunity "
            f"to quote on the following:",
            intro_style
        )
    )

    elements.append(Spacer(1, 8))

    # =================================================
    # PRODUCT TABLE
    # =================================================

    table_data = [[
        "Product",
        "Description",
        "Billing",
        "UOM",
        "Qty",
        "Discount",
        "Unit Price",
        "Total"
    ]]

    for _, row in quote_df.iterrows():

        table_data.append([

            Paragraph(
                f"<b>{str(row['Product'])}</b>",
                normal
            ),

            Paragraph(
                str(row["Description"]),
                normal
            ),

            Paragraph(
                str(row.get("Billing", "")),
                normal
            ),

            Paragraph(
                str(row.get("UOM", "")),
                normal
            ),

            str(row["Qty"]),

            f"{float(row['Discount']):.1f}%",

            f"R {float(row['Unit Price']):,.2f}",

            f"R {float(row['Total']):,.2f}",
        ])

    product_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            28 * mm,  # Product
            52 * mm,  # Description
            18 * mm,  # Billing
            12 * mm,  # UOM
            12 * mm,  # Qty
            18 * mm,  # Discount
            20 * mm,  # Unit Price
            24 * mm,  # Total
        ]
    )

    product_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), BLUE),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),

        ("FONTSIZE", (0, 0), (-1, 0), 7.5),

        ("GRID", (0, 0), (-1, -1), 0.45, colors.grey),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("ALIGN", (3, 1), (4, -1), "CENTER"),

        ("ALIGN", (5, 1), (6, -1), "RIGHT"),

        ("FONTNAME", (0, 1), (-1, -1), FONT_NORMAL),

        ("FONTSIZE", (0, 1), (-1, -1), 7),

        ("TOPPADDING", (0, 0), (-1, -1), 4),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 2))

    # =================================================
    # TOTALS
    # =================================================

    totals_table = Table(
        [
            ["Subtotal:", f"R {subtotal:,.2f}"],
            ["VAT (15%):", f"R {vat:,.2f}"],
            ["Grand Total:", f"R {total:,.2f}"],
        ],
        colWidths=[24 * mm, 24 * mm],
        hAlign="RIGHT"
    )

    totals_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.grey),
        ("BACKGROUND", (0, 2), (-1, 2), LIGHT_BLUE),
        ("FONTNAME", (0, 0), (-1, -1), FONT_BOLD),
        ("TEXTCOLOR", (0, 2), (-1, 2), BLUE),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 4))

    # =================================================
    # TERMS
    # =================================================

    elements.append(
        Paragraph(
            "Terms & Conditions",
            blue_heading
        )
    )

    elements.append(Spacer(1, 1))

    elements.append(
        Paragraph(
            terms,
            normal
        )
    )

    elements.append(Spacer(1, 0))

    # =================================================
    # SIGN OFF
    # =================================================

    line = Table(
        [[""]],
        colWidths=[182 * mm]
    )

    line.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 0.6, BLUE),
    ]))

    elements.append(line)
    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            "Should there be any further information needed, please contact me as above.",
            normal
        )
    )

    elements.append(Spacer(1, 6))

    elements.append(
        Paragraph(
            "Kind regards,",
            normal
        )
    )

    elements.append(Spacer(1, 2))

    try:

        
        if signature_file and os.path.exists(signature_file):

            signature_img = Image(
                signature_file,
                width=35 * mm,
                height=12 * mm
            )

            signature_img.hAlign = "LEFT"

            elements.append(signature_img)
            elements.append(Spacer(1, 2))

    except Exception as e:

        elements.append(
            Paragraph(
                f"SIGNATURE ERROR: {str(e)}",
                normal
            )
        )

    elements.append(
        Paragraph(
            f"<b>{salesperson}</b>",
            normal
        )
    )

    elements.append(
        Paragraph(
            salesperson_phone,
            normal
        )
    )

    elements.append(
        Paragraph(
            salesperson_email,
            normal
        )
    )

    # =================================================
    # BUILD PDF
    # =================================================

    doc.build(
        elements,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer
    )

    return pdf_path