import datetime
from pydantic import BaseModel, HttpUrl

# Pydantic model for the request body when creating a URL
class URLCreate(BaseModel):
    original_url: HttpUrl

# Pydantic model for the response of the /shorten endpoint
class URLInfo(BaseModel):
    original_url: HttpUrl
    shortened_url: str

# Pydantic model for reading URL data from the database
class URL(BaseModel):
    id: int
    clicks: int
    original_url: HttpUrl
    short_code: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True