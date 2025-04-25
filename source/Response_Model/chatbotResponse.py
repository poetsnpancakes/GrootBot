from pydantic import BaseModel


class platform_query(BaseModel):
    query: str
    response:str