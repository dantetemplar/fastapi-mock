from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel

app = FastAPI()

MockUtilities(app)


class ResponseModel(BaseModel):
    message: str


@app.get(
    "/mock-endpoint",
    openapi_extra={
        "examples": [{"message": "My name is (chka-chka, Slim Shady) - Eminem"}]
    },
)
def mock() -> ResponseModel:
    raise NotImplementedError()
