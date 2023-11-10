__all__ = ["MockMiddleware"]

import typing

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
    DispatchFunction,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_501_NOT_IMPLEMENTED
from starlette.types import ASGIApp

from fastapi_mock.exceptions import MockException
from fastapi_mock.example_provider import ExampleProvider


class MockMiddleware(BaseHTTPMiddleware):
    """
    Used to mock the response from the API:

    Return example if MockException is raised
    """

    example_provider: ExampleProvider

    def __init__(
        self,
        app: ASGIApp,
        dispatch: typing.Optional[DispatchFunction] = None,
        example_provider: ExampleProvider = None,
    ) -> None:
        super().__init__(app, dispatch)
        if example_provider is None:
            example_provider = ExampleProvider()
        self.example_provider = example_provider

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await call_next(request)
        except MockException as e:
            try:
                example = self.example_provider.resolve(e.response_model)
                return JSONResponse(content=example, status_code=e.status_code)
            except NotImplementedError:
                return Response(status_code=HTTP_501_NOT_IMPLEMENTED)
