__all__ = ["MockUtilities"]

from random import choice
from typing import Optional, Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from fastapi_mock.example_provider import ExampleProvider
from fastapi_mock.logging_ import logger


class MockUtilities:
    """
    Used to mock the response from the API:

    Will register exception handlers for 501 and 500 errors. If the exception is raised from a route that has an
    example or response_model defined, it will return the example instead of the error.
    """

    HEADERS = {"X-Mock-Response": "1"}

    example_provider: ExampleProvider
    fastapi_app: FastAPI
    return_example_instead_of_501: bool

    def __init__(
            self,
            fastapi_app: FastAPI,
            example_provider: ExampleProvider = None,
            return_example_instead_of_500: bool = False,
    ) -> None:
        if example_provider is None:
            example_provider = ExampleProvider()
        self.fastapi_app = fastapi_app
        self.example_provider = example_provider
        self.return_example_instead_of_500 = return_example_instead_of_500
        self.configure_app()

    def configure_app(self):
        self.fastapi_app.exception_handler(NotImplementedError)(self.dispatch)
        if self.return_example_instead_of_500:
            self.fastapi_app.exception_handler(HTTP_500_INTERNAL_SERVER_ERROR)(
                self.dispatch
            )

    async def dispatch(self, request: Request, exc: Exception):
        try:
            response = self.generate_mock_response(request)
            if response is not None:
                return response
        except Exception as e:
            logger.error(f"Error while mocking response: {e}")
        raise exc

    def generate_mock_response(
            self,
            request: Request,
    ) -> JSONResponse:
        # PRIORITIES:
        resolved_by_example_from_route: tuple[bool, Any] = (False, None)  # 1
        resolved_by_response_model_from_route: tuple[bool, Any] = (False, None)  # 2

        status_code = HTTP_200_OK

        if route := self._get_router_from_request(request):
            if route.openapi_extra is not None:
                if "example" in route.openapi_extra:
                    resolved_by_example_from_route = (
                        True,
                        route.openapi_extra["example"],
                    )
                elif "examples" in route.openapi_extra:
                    resolved_by_example_from_route = (
                        True,
                        choice(route.openapi_extra["examples"]),
                    )

            if route.response_model is not None:
                resolved_by_response_model_from_route = (
                    self._try_resolve_from_response_model(route.response_model)
                )

            if route.status_code is not None:
                status_code = route.status_code

        for is_resolved, content in (
                resolved_by_example_from_route,
                resolved_by_response_model_from_route,
        ):
            if is_resolved:
                return JSONResponse(
                    content=content, status_code=status_code, headers=self.HEADERS
                )

    def _get_router_from_request(self, request: Request) -> Optional[APIRoute]:
        if self.fastapi_app is None:
            return None

        for route in self.fastapi_app.routes:
            if isinstance(route, APIRoute):
                match, scope = route.matches(
                    {
                        "type": "http",
                        "method": request.method,
                        "path": request.url.path,
                    }
                )
                if match == match.FULL:
                    return route
        return None

    def _try_resolve_from_response_model(self, response_model: Any) -> tuple[bool, Any]:
        try:
            return True, self.example_provider.resolve(response_model)
        except NotImplementedError:
            return False, None
