import datetime

from fastapi import FastAPI
from fastapi_mock import MockMiddleware, MockException
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(MockMiddleware)  # add middleware as class, not instance


class ResponseModel(BaseModel):
    message: str = Field(..., example="Hello World!")


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    # instead of ResponseModel, you can use any type annotation that is supported by FastAPI Mock.
    raise MockException(ResponseModel, status_code=200)
