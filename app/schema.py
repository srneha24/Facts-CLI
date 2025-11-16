from pydantic import BaseModel, Field


class Fact(BaseModel):
    fact_id: int = Field(..., description="The database ID of the fact", ge=1)
    fact_text: str = Field(..., description="The text of the fact")
