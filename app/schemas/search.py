from pydantic import BaseModel, Field
from typing import Optional , List


class PacienteSearch(BaseModel):
    keywords: Optional[str] = Field(None, alias="query.term")
    condition: Optional[str] = Field(None, alias="query.cond")
    status: Optional[List[str]] = Field(None, alias="filter.overallStatus")
    location: Optional[str] = Field(None, alias="query.locn")
    intervention: Optional[str] = Field(None, alias="query.intr")
    sponsor: Optional[str] = Field(None, alias="query.lead")
    age: Optional[str] = None  
    sex: Optional[str] = Field(None, alias="eligibilityModule.sex")
    pageToken: Optional[str] = None

    class Config:
        populate_by_name = True