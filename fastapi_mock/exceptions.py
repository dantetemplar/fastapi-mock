__all__ = ["MockException"]

from typing import Any

from starlette.responses import JSONResponse
from starlette.status import HTTP_501_NOT_IMPLEMENTED, HTTP_200_OK


class MockException(UserWarning):
    def __init__(
        self,
        response_model: Any,
        status_code: int = HTTP_200_OK,
        status_code_for_failures: int = HTTP_501_NOT_IMPLEMENTED,
    ):
        self.response_model = response_model
        self.status_code = status_code
        self.status_code_for_failures = status_code_for_failures

    def get_failing_response(self) -> JSONResponse:
        return JSONResponse(
            content={
                "detail": "MockException raised, but no example was provided for this response model."
            },
            status_code=self.status_code_for_failures,
        )


