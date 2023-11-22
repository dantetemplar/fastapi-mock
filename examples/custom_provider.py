from fastapi import FastAPI
from fastapi_mock import MockUtilities, ExampleProvider
from pydantic import BaseModel
from faker import Faker  # pip install faker

app = FastAPI()
fake = Faker()

MockUtilities(
    app, example_provider=ExampleProvider(providers={str: lambda: fake.sentence()})
)


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    raise NotImplementedError()
