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
## Welcome

The AccuSense Quotation System allows users to:

- Create quotations
- Load solution templates
- Add products manually
- Generate PDF quotations
- Submit quotes for approval
- Approve or reject quotations
- Create revisions
- View pending quotations

---

## Creating a Quote

1. Open Create Quote
2. Complete Customer Details
3. Complete Salesperson Details
4. Add products
5. Generate PDF

---

## Loading Solution Templates

1. Expand 'Load Solution Template'
2. Select a template
3. Click Load Template

---

## Adding Products Manually

1. Expand 'Add Products Manually'
2. Select category
3. Select product
4. Enter quantity
5. Click Add To Quote

---

## Quote Approvals

If a quote exceeds your approval limit:

- The quote is submitted for approval
- Approvers review and approve/reject the quote

---

## Revising Quotes

Load an existing quote and save again.

Revision numbers are automatically generated:

Q-20260529-14
Q-20260529-14-R01
Q-20260529-14-R02
Q-20260529-14-R03

---

## My Pending Quotes

View:

- Pending quotes
- Approved quotes
- Rejected quotes

---

## Need Assistance?

Contact the AccuSense administrator.
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