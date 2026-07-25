import re


def validate_invoice(invoice):

    results = []

    # ==========================================
    # 1. INVOICE NUMBER
    # ==========================================

    if invoice.invoice_number:

        results.append(
            (
                "Invoice Number",
                "PASS",
                "Invoice number is available"
            )
        )

    else:

        results.append(
            (
                "Invoice Number",
                "FAILED",
                "Invoice number is missing"
            )
        )


    # ==========================================
    # 2. INVOICE DATE
    # ==========================================

    if invoice.invoice_date:

        results.append(
            (
                "Invoice Date",
                "PASS",
                "Invoice date is available"
            )
        )

    else:

        results.append(
            (
                "Invoice Date",
                "REVIEW",
                "Invoice date is missing"
            )
        )


    # ==========================================
    # 3. VENDOR NAME
    # ==========================================

    if invoice.vendor_name:

        results.append(
            (
                "Vendor Name",
                "PASS",
                "Vendor name is available"
            )
        )

    else:

        results.append(
            (
                "Vendor Name",
                "FAILED",
                "Vendor name is missing"
            )
        )


    # ==========================================
    # 4. VENDOR GSTIN
    # ==========================================

    if invoice.vendor_gstin:

        gstin_pattern = (
            r"^[0-9]{2}"
            r"[A-Z]{5}"
            r"[0-9]{4}"
            r"[A-Z]"
            r"[1-9A-Z]"
            r"Z"
            r"[0-9A-Z]$"
        )

        if re.match(
            gstin_pattern,
            invoice.vendor_gstin.upper()
        ):

            results.append(
                (
                    "Vendor GSTIN",
                    "PASS",
                    "GSTIN format is valid"
                )
            )

        else:

            results.append(
                (
                    "Vendor GSTIN",
                    "REVIEW",
                    "GSTIN format requires review"
                )
            )

    else:

        results.append(
            (
                "Vendor GSTIN",
                "REVIEW",
                "Vendor GSTIN is not available"
            )
        )


    # ==========================================
    # 5. PURCHASE ORDER
    # ==========================================

    if invoice.purchase_order:

        results.append(
            (
                "Purchase Order",
                "PASS",
                "Purchase order is available"
            )
        )

    else:

        results.append(
            (
                "Purchase Order",
                "REVIEW",
                "Purchase order is not available"
            )
        )


    # ==========================================
    # 6. AMOUNT CALCULATION
    #
    # Subtotal - Discount + Tax = Total
    # ==========================================

    if (
        invoice.subtotal is not None
        and invoice.tax is not None
        and invoice.total_amount is not None
    ):

        subtotal = float(
            invoice.subtotal or 0
        )

        discount = float(
            invoice.discount or 0
        )

        tax = float(
            invoice.tax or 0
        )

        total = float(
            invoice.total_amount or 0
        )

        expected_total = (
            subtotal
            - discount
            + tax
        )

        difference = abs(
            expected_total - total
        )

        # ₹1 / currency-unit tolerance
        if difference <= 1:

            results.append(
                (
                    "Amount Calculation",
                    "PASS",
                    (
                        f"Calculated total "
                        f"{expected_total:.2f} matches "
                        f"invoice total {total:.2f}"
                    )
                )
            )

        else:

            results.append(
                (
                    "Amount Calculation",
                    "FAILED",
                    (
                        f"Calculated total is "
                        f"{expected_total:.2f}, "
                        f"but invoice total is "
                        f"{total:.2f}. "
                        f"Difference: {difference:.2f}"
                    )
                )
            )

    else:

        results.append(
            (
                "Amount Calculation",
                "REVIEW",
                "Insufficient amount information for validation"
            )
        )


    # ==========================================
    # RETURN
    # ==========================================

    return results