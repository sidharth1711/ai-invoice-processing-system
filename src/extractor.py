import base64
import os

from openai import OpenAI

from src.models import Invoice


EXTRACTION_PROMPT = """
You are an invoice data extraction system.

Extract all available invoice information accurately.

Important rules:

1. Do not invent missing information.
2. If a field is unavailable, return null.
3. Extract invoice-level information.
4. Extract every visible line item.
5. Preserve invoice numbers and PO numbers exactly.
6. Monetary values must be numbers without currency symbols.
7. Determine the currency from the invoice.
8. GSTIN must be copied exactly as shown.
9. invoice_date should preferably use YYYY-MM-DD format.
10. For each line item, extract any discount shown.
11. If no line-item discount is shown, return null for discount.
"""


def get_client():
    """
    Works locally with .env/environment variable
    and on Streamlit Cloud through environment secrets.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found."
        )

    return OpenAI(api_key=api_key)


def extract_invoice(uploaded_file):

    client = get_client()

    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type

    # ----------------------------------
    # PDF
    # ----------------------------------

    if mime_type == "application/pdf":

        uploaded = client.files.create(
            file=(
                uploaded_file.name,
                file_bytes,
                "application/pdf"
            ),
            purpose="user_data"
        )

        try:

            response = client.responses.parse(
                model="gpt-5",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": uploaded.id
                            },
                            {
                                "type": "input_text",
                                "text": EXTRACTION_PROMPT
                            }
                        ]
                    }
                ],
                text_format=Invoice
            )

            return response.output_parsed

        finally:
            # Do not leave invoice documents stored
            client.files.delete(uploaded.id)

    # ----------------------------------
    # IMAGE
    # ----------------------------------

    image_base64 = base64.b64encode(
        file_bytes
    ).decode("utf-8")

    response = client.responses.parse(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": EXTRACTION_PROMPT
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:{mime_type};base64,"
                            f"{image_base64}"
                        )
                    }
                ]
            }
        ],
        text_format=Invoice
    )

    return response.output_parsed