import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.extractor import extract_invoice
from src.validator import validate_invoice
from src.models import Invoice, LineItem


# ----------------------------------
# Configuration
# ----------------------------------

load_dotenv()

# Streamlit Cloud secrets
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except FileNotFoundError:
    pass


st.set_page_config(
    page_title="AI Invoice Processor",
    page_icon="🧾",
    layout="wide"
)


# ----------------------------------
# Session State
# ----------------------------------

if "invoice" not in st.session_state:
    st.session_state.invoice = None

if "decision" not in st.session_state:
    st.session_state.decision = None


# ----------------------------------
# Header
# ----------------------------------

st.title("🧾 AI Invoice Processing & Validation")

st.caption(
    "AI-powered invoice extraction, validation "
    "and human review."
)

st.info(
    "Portfolio demonstration. Do not upload confidential "
    "or sensitive production invoices."
)


# ----------------------------------
# Upload
# ----------------------------------

uploaded_file = st.file_uploader(
    "Upload an invoice",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ],
    help="Supported formats: PDF, PNG, JPG and JPEG"
)


if uploaded_file:

    file_size = len(uploaded_file.getvalue())

    st.caption(
        f"{uploaded_file.name} • "
        f"{file_size / 1024:.1f} KB"
    )

    # ----------------------------------
    # Preview
    # ----------------------------------

    if uploaded_file.type.startswith("image/"):

        with st.expander(
            "Invoice Preview",
            expanded=True
        ):

            st.image(
                uploaded_file,
                width=700
            )

    else:

        st.success(
            "PDF uploaded successfully."
        )


    # ----------------------------------
    # Extract
    # ----------------------------------

    if st.button(
        "✨ Extract Invoice",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "AI is analysing the invoice..."
            ):

                invoice = extract_invoice(
                    uploaded_file
                )

                st.session_state.invoice = invoice
                st.session_state.decision = None

            st.success(
                "Invoice extracted successfully."
            )

        except Exception as e:

            st.error(
                f"Invoice processing failed: {e}"
            )


# ==================================
# RESULTS
# ==================================

if st.session_state.invoice:

    invoice = st.session_state.invoice

    st.divider()

    st.header("Human Review")

    st.write(
        "Review the extracted information and "
        "correct anything that AI interpreted incorrectly."
    )

    # ----------------------------------
    # Editable Header Fields
    # ----------------------------------

    col1, col2 = st.columns(2)

    with col1:

        invoice_number = st.text_input(
            "Invoice Number",
            value=invoice.invoice_number or ""
        )

        vendor_name = st.text_input(
            "Vendor Name",
            value=invoice.vendor_name or ""
        )

        vendor_gstin = st.text_input(
            "Vendor GSTIN",
            value=invoice.vendor_gstin or ""
        )

        customer_name = st.text_input(
            "Customer Name",
            value=invoice.customer_name or ""
        )

        customer_gstin = st.text_input(
            "Customer GSTIN",
            value=invoice.customer_gstin or ""
        )


    with col2:

        invoice_date = st.text_input(
            "Invoice Date",
            value=invoice.invoice_date or ""
        )

        purchase_order = st.text_input(
            "Purchase Order",
            value=invoice.purchase_order or ""
        )

        subtotal = st.number_input(
            "Subtotal",
            value=float(invoice.subtotal or 0),
            step=1.0
        )

        tax = st.number_input(
            "Tax",
            value=float(invoice.tax or 0),
            step=1.0
        )

        total_amount = st.number_input(
            "Total Amount",
            value=float(invoice.total_amount or 0),
            step=1.0
        )

        currency = st.text_input(
            "Currency",
            value=invoice.currency or ""
        )


    # ----------------------------------
    # Line Items
    # ----------------------------------

    st.subheader("Line Items")

    if invoice.line_items:

        line_items_df = pd.DataFrame(
            [
                item.model_dump()
                for item in invoice.line_items
            ]
        )

    else:

        line_items_df = pd.DataFrame(
            columns=[
                "description",
                "quantity",
                "unit_price",
                "tax",
                "amount"
            ]
        )


    edited_line_items = st.data_editor(
        line_items_df,
        num_rows="dynamic",
        use_container_width=True
    )


    # ----------------------------------
    # Create reviewed invoice
    # ----------------------------------

    reviewed_line_items = []

    for _, row in edited_line_items.iterrows():

        reviewed_line_items.append(
            LineItem(
                description=row.get("description"),
                quantity=row.get("quantity"),
                unit_price=row.get("unit_price"),
                tax=row.get("tax"),
                amount=row.get("amount")
            )
        )


    reviewed_invoice = Invoice(
        invoice_number=invoice_number or None,
        invoice_date=invoice_date or None,

        vendor_name=vendor_name or None,
        vendor_gstin=vendor_gstin or None,

        customer_name=customer_name or None,
        customer_gstin=customer_gstin or None,

        purchase_order=purchase_order or None,

        subtotal=subtotal,
        tax=tax,
        total_amount=total_amount,
        currency=currency or None,

        line_items=reviewed_line_items
    )


    # ==================================
    # VALIDATION
    # ==================================

    st.divider()

    st.header("Validation Results")

    overall_status, validation_results = (
        validate_invoice(reviewed_invoice)
    )


    if overall_status == "PASS":

        st.success(
            "✓ PASS — Invoice passed validation."
        )

    elif overall_status == "REVIEW":

        st.warning(
            "⚠ REVIEW — Some fields require human review."
        )

    else:

        st.error(
            "✕ FAILED — Invoice failed validation."
        )


    validation_df = pd.DataFrame(
        validation_results,
        columns=[
            "Check",
            "Status",
            "Details"
        ]
    )

    st.dataframe(
        validation_df,
        use_container_width=True,
        hide_index=True
    )


    # ==================================
    # DECISION
    # ==================================

    st.divider()

    st.header("Decision")

    approve_col, reject_col = st.columns(2)


    with approve_col:

        if st.button(
            "✓ Approve Invoice",
            type="primary",
            use_container_width=True
        ):

            if overall_status == "FAILED":

                st.error(
                    "Resolve failed validations before approval."
                )

            else:

                st.session_state.decision = "APPROVED"


    with reject_col:

        if st.button(
            "✕ Reject Invoice",
            use_container_width=True
        ):

            st.session_state.decision = "REJECTED"


    # ----------------------------------
    # Decision Result
    # ----------------------------------

    if st.session_state.decision == "APPROVED":

        st.success(
            "Invoice approved."
        )

    elif st.session_state.decision == "REJECTED":

        st.error(
            "Invoice rejected."
        )


    # ==================================
    # EXPORT
    # ==================================

    if st.session_state.decision == "APPROVED":

        st.divider()

        st.header("Export")

        export_data = {
            "invoice_number":
                reviewed_invoice.invoice_number,

            "invoice_date":
                reviewed_invoice.invoice_date,

            "vendor_name":
                reviewed_invoice.vendor_name,

            "vendor_gstin":
                reviewed_invoice.vendor_gstin,

            "customer_name":
                reviewed_invoice.customer_name,

            "customer_gstin":
                reviewed_invoice.customer_gstin,

            "purchase_order":
                reviewed_invoice.purchase_order,

            "subtotal":
                reviewed_invoice.subtotal,

            "tax":
                reviewed_invoice.tax,

            "total_amount":
                reviewed_invoice.total_amount,

            "currency":
                reviewed_invoice.currency,

            "validation_status":
                overall_status,

            "approval_status":
                "APPROVED"
        }


        export_df = pd.DataFrame(
            [export_data]
        )


        csv_data = export_df.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            "⬇ Download Invoice CSV",
            data=csv_data,
            file_name="approved_invoice.csv",
            mime="text/csv",
            use_container_width=True
        )


        # ----------------------------------
        # Line Item Export
        # ----------------------------------

        if reviewed_invoice.line_items:

            lines_df = pd.DataFrame(
                [
                    item.model_dump()
                    for item
                    in reviewed_invoice.line_items
                ]
            )

            lines_csv = lines_df.to_csv(
                index=False
            ).encode("utf-8")


            st.download_button(
                "⬇ Download Line Items CSV",
                data=lines_csv,
                file_name="invoice_line_items.csv",
                mime="text/csv",
                use_container_width=True
            )


# ----------------------------------
# Footer
# ----------------------------------

st.divider()

st.caption(
    "AI Invoice Processing & Validation System • "
    "Built with Python, OpenAI, Pydantic and Streamlit"
)