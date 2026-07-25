import re


def validate_invoice(invoice):

    results = []

    # Invoice Number
    if invoice.invoice_number:
        results.append(
            ("Invoice Number", "PASS", "Invoice number available")
        )
    else:
        results.append(
            ("Invoice Number", "FAIL", "Invoice number missing")
        )

    # Invoice Date
    if invoice.invoice_date:
        results.append(
            ("Invoice Date", "PASS", "Invoice date available")
        )
    else:
        results.append(
            ("Invoice Date", "REVIEW", "Invoice date missing")
        )

    # Vendor
    if invoice.vendor_name:
        results.append(
            ("Vendor", "PASS", "Vendor identified")
        )
    else:
        results.append(
            ("Vendor", "FAIL", "Vendor missing")
        )

    # GSTIN validation
    if invoice.vendor_gstin:

        gst_pattern = (
            r"^[0-9]{2}[A-Z]{5}[0-9]{4}"
            r"[A-Z][1-9A-Z]Z[0-9A-Z]$"
        )

        if re.match(gst_pattern, invoice.vendor_gstin.upper()):

            results.append(
                ("GSTIN", "PASS", "GSTIN format valid")
            )

        else:

            results.append(
                ("GSTIN", "REVIEW", "GSTIN format requires review")
            )

    else:

        results.append(
            ("GSTIN", "REVIEW", "GSTIN not detected")
        )

    # PO Number
    if invoice.purchase_order:

        results.append(
            ("Purchase Order", "PASS", "PO number available")
        )

    else:

        results.append(
            ("Purchase Order", "REVIEW", "PO number not detected")
        )

    # Amount validation
    if (
        invoice.subtotal is not None
        and invoice.tax is not None
        and invoice.total_amount is not None
    ):

        expected_total = invoice.subtotal + invoice.tax

        difference = abs(
            expected_total - invoice.total_amount
        )

        if difference <= 1:

            results.append(
                (
                    "Amount Calculation",
                    "PASS",
                    "Subtotal + Tax matches Total"
                )
            )

        else:

            results.append(
                (
                    "Amount Calculation",
                    "FAIL",
                    f"Amount mismatch: difference {difference:.2f}"
                )
            )

    else:

        results.append(
            (
                "Amount Calculation",
                "REVIEW",
                "Unable to validate invoice total"
            )
        )

    # Determine overall status
    statuses = [result[1] for result in results]

    if "FAIL" in statuses:
        overall_status = "FAILED"

    elif "REVIEW" in statuses:
        overall_status = "REVIEW"

    else:
        overall_status = "PASS"

    return overall_status, results