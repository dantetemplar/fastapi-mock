from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel, Field

app = FastAPI()

MockUtilities(app)


class ResponseModel(BaseModel):
    field_with_examples: str = Field(examples=["I", "Love", "Python"])
    field_with_default: str = Field(default="I ❤️ Python")
    field_with_default_factory: str = Field(default_factory=lambda: "I ❤️ Python\n" * 3)


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    raise NotImplementedError()
