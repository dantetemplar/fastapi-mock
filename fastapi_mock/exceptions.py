__all__ = ["MockException"]

from typing import Any

from starlette.exceptions import HTTPException


class MockException(HTTPException):
    def __init__(self, response_model: Any, status_code: int = 200):
        self.response_model = response_model
        self.status_code = status_code

        super().__init__(status_code=status_code, detail="Mocked response, see docs for more info")
