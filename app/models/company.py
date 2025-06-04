from pydantic import BaseModel, ConfigDict, Field

class CompanyInfo(BaseModel):
    company_name: str = Field(..., alias="Company Name")
    pic_name: str = Field("(not shown)", alias="PIC Name")
    pic_position: str = Field("(not shown)", alias="PIC Position")
    emails: list[str] = Field("(not shown)", alias="Email(s)")

    model_config = ConfigDict(validate_by_name=True, extra="ignore")