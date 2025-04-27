from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Identifier(BaseModel):
    id: str
    scheme: str
    legal_name: str = Field(alias="legalName")
    legal_name_en: Optional[str] = Field(default=None, alias="legalName_en")


class Address(BaseModel):
    street_address: str = Field(alias="streetAddress")
    postal_code: str = Field(alias="postalCode")
    locality: str
    country_name: str = Field(alias="countryName")


class ContactPoint(BaseModel):
    name: str
    telephone: str
    email: str
    name_en: Optional[str] = Field(default=None, alias="name_en")


class ProcuringEntity(BaseModel):
    identifier: Identifier
    address: Address
    contact_point: ContactPoint = Field(alias="contactPoint")
    kind: str
    name: str
    name_en: Optional[str] = Field(default=None, alias="name_en")


class Period(BaseModel):
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    clarifications_until: Optional[datetime] = Field(default=None, alias="clarificationsUntil")
    invalidation_date: Optional[datetime] = Field(default=None, alias="invalidationDate")


class Value(BaseModel):
    amount: float
    value_added_tax_included: bool = Field(alias="valueAddedTaxIncluded")
    currency: str


class Tender(BaseModel):
    procuring_entity: ProcuringEntity = Field(alias="procuringEntity")
    enquiry_period: Optional[Period] = Field(default=None, alias="enquiryPeriod")
    tender_period: Optional[Period] = Field(default=None, alias="tenderPeriod")
    title: str
    tender_id: str = Field(alias="tenderID")
    value: Value
    status: str


class TenderSearchResponse(BaseModel):
    page: int
    per_page: int = Field(alias="per_page")
    total: int
    data: List[Tender]


class SearchParams(BaseModel):
    text: Optional[str] = None
    region: Optional[str] = None
    page: int = 0
    per_page: int = 20 