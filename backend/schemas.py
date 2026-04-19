from typing import List, Optional
from pydantic import BaseModel

class AppointmentIn(BaseModel):
    label: str
    value: str

class PaymentIn(BaseModel):
    label: str
    value: str

class FabricIn(BaseModel):
    name: str
    use: str
    qty: str
    price: str
    to_buy: bool = False
    supplier: str = ""

class ClientCreate(BaseModel):
    name: str
    wedding_date: str
    days_until: int
    status: str
    garment: str = ""
    garment_style: str = ""
    measurements_date: str = ""
    phone: str = ""
    email: str = ""
    notes: str = ""
    appointments: List[AppointmentIn] = []
    payments: List[PaymentIn] = []
    fabrics: List[FabricIn] = []

class ClientPatch(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    days_until: Optional[int] = None
    wedding_date: Optional[str] = None
    wedding_date_iso: Optional[str] = None
    garment: Optional[str] = None
    garment_style: Optional[str] = None
    measurements_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
