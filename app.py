import base64
from io import BytesIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.extractor import extract_invoice
from src.validator import validate_invoice
from src.models import Invoice, LineItem


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="AI Invoice Processing System",
    page_icon="🧾",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "invoice" not in st.session_state:
    st.session_state.invoice = None

if "decision" not in st.session_state:
    st.session_state.decision = None

if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None

if "uploaded_file_type" not in st.session_state:
    st.session_state.uploaded_file_type = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


# ============================================================
# HEADER
# ============================================================

st.title("🧾 AI Invoice Processing & Validation System")

st.markdown(
    """
    Upload an invoice and use AI to extract structured information,
    review the extracted data, validate business rules and export
    the approved invoice.

    **Upload → Extract → Review → Validate → Approve → Export**
    """
)

st.info(
    "Portfolio demonstration. Please do not upload confidential "
    "or sensitive production invoices."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("About")

    st.write(
        """
        AI-powered invoice processing application demonstrating:

        • Multimodal AI extraction  
        • Structured outputs  
        • Human-in-the-loop review  
        • Business-rule validation  
        • Approval workflow  
        • Excel export
        """
    )

    st.subheader("Technology")

    st.write(
        """
        • Python  
        • OpenAI API  
        • Pydantic  
        • Streamlit  
        • Pandas
        """
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Invoice",
    type=["pdf", "png", "jpg", "jpeg"]
)


# ============================================================
# FILE SIZE VALIDATION
# ============================================================

MAX_FILE_SIZE_MB = 5

if uploaded_file is not None:

    uploaded_bytes = uploaded_file.getvalue()

    file_size_mb = (
        len(uploaded_bytes) / (1024 * 1024)
    )

    if file_size_mb > MAX_FILE_SIZE_MB:

        st.error(
            f"File too large. Maximum file size is "
            f"{MAX_FILE_SIZE_MB} MB."
        )

        st.stop()


# ============================================================
# EXTRACT BUTTON
# ============================================================

if uploaded_file is not None:

    if st.button(
        "🤖 Extract Invoice",
        type="primary",
        use_container_width=True
    ):

        try:

            # ----------------------------------------------
            # SAVE ORIGINAL DOCUMENT FOR REVIEW
            # ----------------------------------------------

            st.session_state.uploaded_file_bytes = (
                uploaded_file.getvalue()
            )

            st.session_state.uploaded_file_type = (
                uploaded_file.type
            )

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )


            # ----------------------------------------------
            # AI EXTRACTION
            # ----------------------------------------------

            with st.spinner(
                "AI is reading the invoice..."
            ):

                invoice = extract_invoice(
                    uploaded_file
                )

                st.session_state.invoice = invoice

                # Reset previous approval/rejection
                st.session_state.decision = None


            st.success(
                "Invoice extracted successfully."
            )

        except Exception as e:

            st.error(
                f"Invoice extraction failed: {e}"
            )


# ============================================================
# CONTINUE ONLY AFTER EXTRACTION
# ============================================================

if st.session_state.invoice is not None:

    invoice = st.session_state.invoice

    st.divider()

    st.header("Human Review")

    st.caption(
        "Compare the original invoice with the AI-extracted "
        "information and correct any values if required."
    )


    # ========================================================
    # SIDE-BY-SIDE REVIEW
    # ========================================================

    document_col, fields_col = st.columns(
        [1.15, 1],
        gap="large"
    )


    # ========================================================
    # LEFT SIDE — ORIGINAL DOCUMENT
    # ========================================================

    with document_col:

        st.subheader("📄 Original Invoice")

        file_bytes = (
            st.session_state.uploaded_file_bytes
        )

        file_type = (
            st.session_state.uploaded_file_type
        )

        file_name = (
            st.session_state.uploaded_file_name
        )


        if file_bytes is None:

            st.warning(
                "Original document preview is unavailable. "
                "Please upload and extract the invoice again."
            )


        # ----------------------------------------------------
        # IMAGE PREVIEW
        # ----------------------------------------------------

        elif file_type in [
            "image/png",
            "image/jpeg",
            "image/jpg"
        ]:

            st.image(
                file_bytes,
                caption=file_name,
                use_container_width=True
            )


        # ----------------------------------------------------
        # PDF PREVIEW
        # ----------------------------------------------------

        elif file_type == "application/pdf":

            base64_pdf = base64.b64encode(
                file_bytes
            ).decode("utf-8")

            pdf_html = f"""
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="900px"
                style="border: 1px solid #ddd;
                       border-radius: 8px;">
            </iframe>
            """

            st.markdown(
                pdf_html,
                unsafe_allow_html=True
            )

            st.caption(
                f"Original document: {file_name}"
            )


        else:

            st.warning(
                "Preview is not available for this file type."
            )


    # ========================================================
    # RIGHT SIDE — EXTRACTED HEADER FIELDS
    # ========================================================

    with fields_col:

        st.subheader("📝 Extracted Invoice Data")

        invoice_number = st.text_input(
            "Invoice Number",
            value=invoice.invoice_number or ""
        )

        invoice_date = st.text_input(
            "Invoice Date",
            value=invoice.invoice_date or ""
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

        purchase_order = st.text_input(
            "Purchase Order",
            value=invoice.purchase_order or ""
        )

        subtotal = st.number_input(
            "Subtotal",
            value=float(invoice.subtotal or 0),
            step=1.0,
            format="%.2f"
        )

        discount = st.number_input(
            "Discount",
            value=float(invoice.discount or 0),
            step=1.0,
            format="%.2f"
        )

        tax = st.number_input(
            "Tax",
            value=float(invoice.tax or 0),
            step=1.0,
            format="%.2f"
        )

        total_amount = st.number_input(
            "Total Amount",
            value=float(invoice.total_amount or 0),
            step=1.0,
            format="%.2f"
        )

        currency = st.text_input(
            "Currency",
            value=invoice.currency or ""
        )


    # ========================================================
    # LINE ITEMS
    # ========================================================

    st.divider()

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


    # ========================================================
    # KEEP ONLY EXPECTED LINE-ITEM COLUMNS
    # ========================================================

    expected_columns = [
        "description",
        "quantity",
        "unit_price",
        "tax",
        "amount"
    ]

    for column in expected_columns:

        if column not in line_items_df.columns:
            line_items_df[column] = None

    line_items_df = line_items_df[
        expected_columns
    ]


    # ========================================================
    # EDITABLE LINE ITEMS
    # ========================================================

    edited_line_items = st.data_editor(
        line_items_df,
        num_rows="dynamic",
        use_container_width=True,
        key="line_items_editor"
    )


    # ========================================================
    # REBUILD LINE ITEMS
    # ========================================================

    reviewed_line_items = []

    for _, row in edited_line_items.iterrows():

        if row.isna().all():
            continue

        reviewed_line_items.append(
            LineItem(

                description=(
                    None
                    if pd.isna(
                        row.get("description")
                    )
                    else str(
                        row.get("description")
                    )
                ),

                quantity=(
                    None
                    if pd.isna(
                        row.get("quantity")
                    )
                    else float(
                        row.get("quantity")
                    )
                ),

                unit_price=(
                    None
                    if pd.isna(
                        row.get("unit_price")
                    )
                    else float(
                        row.get("unit_price")
                    )
                ),

                tax=(
                    None
                    if pd.isna(
                        row.get("tax")
                    )
                    else float(
                        row.get("tax")
                    )
                ),

                amount=(
                    None
                    if pd.isna(
                        row.get("amount")
                    )
                    else float(
                        row.get("amount")
                    )
                )
            )
        )


    # ========================================================
    # CREATE REVIEWED INVOICE
    # ========================================================

    reviewed_invoice = Invoice(

        invoice_number=(
            invoice_number or None
        ),

        invoice_date=(
            invoice_date or None
        ),

        vendor_name=(
            vendor_name or None
        ),

        vendor_gstin=(
            vendor_gstin or None
        ),

        customer_name=(
            customer_name or None
        ),

        customer_gstin=(
            customer_gstin or None
        ),

        purchase_order=(
            purchase_order or None
        ),

        subtotal=subtotal,

        discount=discount,

        tax=tax,

        total_amount=total_amount,

        currency=(
            currency or None
        ),

        line_items=reviewed_line_items
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    st.divider()

    st.header("Validation")

    try:

        validation_results = validate_invoice(
            reviewed_invoice
        )

    except Exception as e:

        st.error(
            f"Validation failed: {e}"
        )

        st.stop()


    # ========================================================
    # VALIDATION TABLE
    # ========================================================

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


    # ========================================================
    # OVERALL STATUS
    # ========================================================

    statuses = [
        str(result[1]).upper()
        for result in validation_results
    ]


    if any(
        status in ["FAIL", "FAILED"]
        for status in statuses
    ):

        overall_status = "FAILED"

        st.error(
            "❌ Invoice validation failed."
        )


    elif any(
        status == "REVIEW"
        for status in statuses
    ):

        overall_status = "REVIEW"

        st.warning(
            "⚠️ Invoice requires human review."
        )


    else:

        overall_status = "PASS"

        st.success(
            "✅ Invoice passed validation."
        )


    # ========================================================
    # AMOUNT SUMMARY
    # ========================================================

    st.subheader("Amount Summary")

    amount_col1, amount_col2, amount_col3, amount_col4 = (
        st.columns(4)
    )

    amount_col1.metric(
        "Subtotal",
        f"{subtotal:,.2f}"
    )

    amount_col2.metric(
        "Discount",
        f"{discount:,.2f}"
    )

    amount_col3.metric(
        "Tax",
        f"{tax:,.2f}"
    )

    amount_col4.metric(
        "Total",
        f"{total_amount:,.2f}"
    )


    expected_total = (
        subtotal
        - discount
        + tax
    )


    st.caption(
        f"Calculated Total: "
        f"{subtotal:,.2f} - "
        f"{discount:,.2f} + "
        f"{tax:,.2f} = "
        f"{expected_total:,.2f}"
    )


    # ========================================================
    # HUMAN DECISION
    # ========================================================

    st.divider()

    st.header("Human Decision")

    decision_col1, decision_col2 = (
        st.columns(2)
    )


    with decision_col1:

        if st.button(
            "✅ Approve Invoice",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.decision = (
                "APPROVED"
            )


    with decision_col2:

        if st.button(
            "❌ Reject Invoice",
            use_container_width=True
        ):

            st.session_state.decision = (
                "REJECTED"
            )


    # ========================================================
    # DECISION MESSAGE
    # ========================================================

    if (
        st.session_state.decision
        == "APPROVED"
    ):

        st.success(
            "Invoice approved."
        )


    elif (
        st.session_state.decision
        == "REJECTED"
    ):

        st.error(
            "Invoice rejected."
        )


    # ========================================================
    # EXPORT
    # ========================================================

    if (
        st.session_state.decision
        == "APPROVED"
    ):

        st.divider()

        st.header("Export")


        # ====================================================
        # INVOICE HEADER EXPORT
        # ====================================================

        header_data = {

            "Invoice Number":
                reviewed_invoice.invoice_number,

            "Invoice Date":
                reviewed_invoice.invoice_date,

            "Vendor Name":
                reviewed_invoice.vendor_name,

            "Vendor GSTIN":
                reviewed_invoice.vendor_gstin,

            "Customer Name":
                reviewed_invoice.customer_name,

            "Customer GSTIN":
                reviewed_invoice.customer_gstin,

            "Purchase Order":
                reviewed_invoice.purchase_order,

            "Subtotal":
                reviewed_invoice.subtotal,

            "Discount":
                reviewed_invoice.discount,

            "Tax":
                reviewed_invoice.tax,

            "Total Amount":
                reviewed_invoice.total_amount,

            "Currency":
                reviewed_invoice.currency,

            "Validation Status":
                overall_status,

            "Approval Status":
                "APPROVED"
        }


        header_df = pd.DataFrame(
            [header_data]
        )


        # ====================================================
        # LINE ITEM EXPORT
        # ====================================================

        if reviewed_invoice.line_items:

            lines_df = pd.DataFrame(
                [
                    item.model_dump()
                    for item
                    in reviewed_invoice.line_items
                ]
            )

        else:

            lines_df = pd.DataFrame(
                columns=[
                    "description",
                    "quantity",
                    "unit_price",
                    "tax",
                    "amount"
                ]
            )


        # ====================================================
        # VALIDATION EXPORT
        # ====================================================

        validation_export_df = pd.DataFrame(
            validation_results,
            columns=[
                "Check",
                "Status",
                "Details"
            ]
        )


        # ====================================================
        # CREATE EXCEL WORKBOOK
        # ====================================================

        excel_buffer = BytesIO()


        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            header_df.to_excel(
                writer,
                sheet_name="Invoice Header",
                index=False
            )

            lines_df.to_excel(
                writer,
                sheet_name="Line Items",
                index=False
            )

            validation_export_df.to_excel(
                writer,
                sheet_name="Validation Results",
                index=False
            )


        excel_buffer.seek(0)


        # ====================================================
        # SAFE FILE NAME
        # ====================================================

        invoice_number_for_file = (
            reviewed_invoice.invoice_number
            or "invoice"
        )


        safe_invoice_number = "".join(
            character
            for character
            in invoice_number_for_file
            if (
                character.isalnum()
                or character in ("-", "_")
            )
        )


        if not safe_invoice_number:

            safe_invoice_number = "invoice"


        file_name = (
            f"{safe_invoice_number}"
            f"_processed.xlsx"
        )


        # ====================================================
        # DOWNLOAD
        # ====================================================

        st.download_button(
            label=(
                "⬇ Download Complete Invoice"
            ),

            data=excel_buffer.getvalue(),

            file_name=file_name,

            mime=(
                "application/vnd."
                "openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),

            use_container_width=True
        )


        st.caption(
            "Excel workbook includes Invoice Header, "
            "Line Items and Validation Results."
        )