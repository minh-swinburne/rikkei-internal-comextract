from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
import datetime

class InvoiceItem(BaseModel):
    id: str = Field(..., alias="ID")
    description: str = Field(..., alias="Description")
    ordered_quantity: int = Field(..., alias="Ordered Quantity")
    shipped_quantity: Optional[int] = Field(None, alias="Shipped Quantity")
    unit_price: float = Field(..., alias="Unit Price")
    total_price: float = Field(..., alias="Total Price")

    model_config = ConfigDict(validate_by_name=True, extra="ignore")


class Invoice(BaseModel):
    id: str = Field(..., alias="ID")
    date: str = Field(..., alias="Date")
    seller: str = Field(..., alias="Seller")
    buyer: str = Field(..., alias="Buyer")
    items: list[InvoiceItem] = Field(..., alias="Items")
    net_price: float = Field(..., alias="Net Price")
    total_price: float = Field(..., alias="Total Price")

    model_config = ConfigDict(validate_by_name=True, extra="ignore")
