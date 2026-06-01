import streamlit as st
from modules.auth import require_login
from modules.ui import render_header

st.set_page_config(
    page_title="Help & User Manual",
    layout="wide"
)

require_login()

render_header()

st.title("📖 Help & User Manual")

st.markdown("""
# AccuSense Quotation System User Guide

The AccuSense Quotation System is used to create, manage, revise, approve and issue customer quotations.

---

## 1. Login

1. Open the AccuSense Quotation System.
2. Enter your email address and password.
3. Click **Login**.

After login your name and role will appear in the sidebar.

---

## 2. Creating a New Quote

1. Open **Create Quote**.
2. Complete:
   - Customer Name
   - Company
   - Site
   - Salesperson Name
   - Salesperson Phone
   - Salesperson Email

3. Add products using either:
   - Load Solution Template
   - Add Products Manually

---

## 3. Loading Solution Templates

Solution Templates allow commonly used systems to be loaded quickly.

### Steps

1. Expand **Load Solution Template**
2. Select the required template
3. Click **Load Template Into Quote**

The products from the template will automatically be added to the quote.

---

## 4. Adding Products Manually

Use this option for custom quotations.

### Steps

1. Expand **Add Products Manually**
2. Select the Main Category
3. Select the Product
4. Enter Quantity
5. Enter Discount if applicable
6. Click **Add To Quote**

The item will be added to the quote summary.

---

## 5. Quote Summary

The Quote Summary displays all items currently included in the quotation.

Users may:

- Edit quantities
- Edit discounts
- Remove items
- Review profitability

The quote totals are automatically recalculated.

---

## 6. Annual Monitoring Fee

When sensor products are included in a quote, the system automatically adds an Annual Monitoring Fee.

The fee is calculated from the Monitoring Fee product configured in the Products sheet.

The fee is automatically updated based on the total number of sensors included.

In summarized quotations the monitoring fee appears under the Identification configured in the Products sheet, for example:

Service - Monitoring

---

## 7. Quote Output Type

Before generating a PDF, select the required output format.

### Summarized Quote (Default)

This is the default option.

Products are grouped according to the Identification column from the Products sheet.

This format is recommended for customer quotations where a simple overview is preferred.

### Detailed Quote

Displays all individual products and line items.

This format is useful when customers require a complete product breakdown.

---

## 8. Generating a Quote PDF

Once the quote is complete:

1. Select the required Quote Output Type
2. Click **Generate / Save PDF**
3. Download the generated PDF

The PDF includes:

- Quote Number
- Customer Details
- Salesperson Details
- Product Table
- Totals
- Terms & Conditions
- Salesperson Signature (if configured)

### PDF Layout Notes

The Billing column is hidden on PDF quotations.

The Discount column is hidden on PDF quotations.

These fields remain available inside the quotation editor.

---

## 9. Salesperson Signatures

Users may have a signature assigned through the Users sheet.

### Users Sheet Column

Signature File

### Example

signatures/eddie_signature.png

When configured, the signature is automatically displayed above the salesperson name on the PDF quotation.

---

## 10. Loading Existing Quotes

Use the sidebar option:

Load Existing Quote

to recall a previously saved quotation.

Loading an existing quote does NOT automatically create a revision.

The original quote number is retained.

---

## 11. Download Existing PDF

After loading an existing quote, users may select:

Download Existing PDF

This downloads the existing PDF using the original quote number.

No revision is created.

Example:

Q-20260601-10

remains

Q-20260601-10

---

## 12. Create Revision

If changes are required to an existing quote:

1. Load the quote
2. Click **Create Revision**
3. Make the required changes
4. Generate the new PDF

The revision number automatically increments.

### Examples

Original Quote

Q-20260601-10

First Revision

Q-20260601-10-R01

Second Revision

Q-20260601-10-R02

Third Revision

Q-20260601-10-R03

Revision numbers only increase when Create Revision is selected.

---

## 13. Approval Workflow

The system supports approval limits.

If the quote value exceeds your approval limit:

- The quote is submitted for approval
- Approval is required before the quote can be issued

Approvers can review the quote and either:

- Approve
- Reject

---

## 14. Approvals Page

Authorised users may access:

Approvals

to:

- Review approval requests
- View quote details
- Approve quotations
- Reject quotations
- Add approval notes

---

## 15. My Pending Quotes

Users may view:

My Pending Quotes

to see:

- Pending approvals
- Approved quotations
- Rejected quotations
- Approval comments

---

## 16. Sales Report

Users with permission can access:

Sales Report

This page provides reporting and sales information.

Access is controlled through the Users sheet.

---

## 17. Troubleshooting

### Product Not Found

Verify that the product exists in the Products sheet.

### Missing Required Information

Customer Name, Company and Salesperson Name are required before a quote can be generated.

### Approval Required

The quote value exceeds your approval limit.

### Existing PDF Not Found

The quote exists but the PDF file cannot be located.

Generate a new PDF if required.

### Monitoring Fee Missing

Verify that the Monitoring Fee product exists in the Products sheet.

---

## 18. Support

For support, configuration changes or user access requests, contact the AccuSense system administrator.
""")

try:
    with open(
        "docs/AccuSense_User_Manual.pdf",
        "rb"
    ) as pdf_file:

        st.download_button(
            "📥 Download User Manual (PDF)",
            pdf_file,
            file_name="AccuSense_User_Manual.pdf",
            mime="application/pdf"
        )

except Exception:
    st.warning(
        "User manual PDF not found."
    )