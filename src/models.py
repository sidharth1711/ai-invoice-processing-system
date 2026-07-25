from pydantic import BaseModel, Field
from typing import Optional


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    tax: Optional[float] = None
    amount: Optional[float] = None


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None

    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None

    customer_name: Optional[str] = None
    customer_gstin: Optional[str] = None

    purchase_order: Optional[str] = None

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None

    line_items: list[LineItem] = Field(default_factory=list)