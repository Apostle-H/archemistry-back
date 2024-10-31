import logging

from pydantic import BaseModel


class APIException(Exception):
    def __init__(self, error: str, status_code: int = 400):
        self.error = error
        self.status_code = status_code


class APIExceptionModel(BaseModel):
    error: str
    status_code: int

    class Config:
        json_schema_extra = {"example": {"error": "Not found", "status_code": 404}}
