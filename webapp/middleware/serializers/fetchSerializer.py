from pydantic import BaseModel
from typing import Optional

class FetchSerializer(BaseModel):
    class FetchResponse(BaseModel):
        id: int
        data_product_name: str
        category: Optional[str]
        status: Optional[str]
        created_at: Optional[str]
        updated_at: Optional[str]
        owner: Optional[str]
        description: Optional[str]
