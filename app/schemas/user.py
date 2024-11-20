from pydantic import BaseModel, EmailStr, Field 
from typing import Optional 

class UpdateUser(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[str] = None 