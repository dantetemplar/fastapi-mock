from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel

app = FastAPI()

# just create an instance of MockUtilities and pass FastAPI app as argument to it. It will add exception handlers to
# the app automatically.
MockUtilities(app, return_example_instead_of_500=True)


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint", status_code=200)
def mock() -> ResponseModel:
    # instead of ResponseModel, you can use any type annotation that is supported by FastAPI Mock.
    raise NotImplementedError()
