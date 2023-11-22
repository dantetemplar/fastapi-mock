from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel, ConfigDict

app = FastAPI()

MockUtilities(app)


class ResponseModel(BaseModel):
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"message": "My name is (chka-chka, Slim Shady) - Eminem"}]
        }
    )


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    raise NotImplementedError()
