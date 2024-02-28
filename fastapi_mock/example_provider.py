__all__ = ["ExampleProvider"]

import random
import types
from enum import Enum
from random import choice
from types import NoneType, GenericAlias, UnionType
from typing import Any, Callable

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

PROVIDER_TYPE = Callable[[], Any] | Callable[[type], Any] | Any

DEFAULT_PROVIDERS: dict[type, PROVIDER_TYPE] = {
    bool: lambda: bool(random.getrandbits(1)),
    int: lambda: random.randrange(0, 100),
    float: lambda: random.uniform(0, 100),
    str: "Hello, World ❤️",
    Enum: lambda enumeration: choice(list(enumeration.__members__.values())),
}


class ExampleProvider:
    _providers: dict[type, PROVIDER_TYPE]

    def __init__(
            self,
            providers: dict[type, PROVIDER_TYPE] = None,
    ):
        self._providers = dict()

        if providers is None:
            providers = DEFAULT_PROVIDERS.copy()

        for type_, provider in providers.items():
            self.register_provider(type_, provider)

    @property
    def registered_types(self):
        return tuple(self._providers.keys())

    def register_provider(self, type_: type, provider: PROVIDER_TYPE):
        if not isinstance(type_, type):
            raise TypeError(f"{type_} is not a `type`, but `{type(type_)}`")

        if issubclass(type_, BaseModel):
            raise TypeError(
                f"{type_} is a pydantic model, if you want to change logic for it, inherit from "
                f"ExampleProvider and override _resolve_for_pydantic_model method."
            )

        if type_ is NoneType or type_ is None:
            raise TypeError(
                f"{type_} is a NoneType, if you want to change logic for it, inherit from "
                f"ExampleProvider and override _resolve_for_registered_type method."
            )

        self._providers[type_] = provider

    def resolve(self, annotation: type[Any] | None) -> Any:
        if isinstance(annotation, type):
            if issubclass(annotation, self.registered_types):
                return self._resolve_for_registered_type(annotation)
            elif issubclass(annotation, BaseModel):
                return self._resolve_for_pydantic_model(annotation)

        elif isinstance(annotation, GenericAlias):
            origin, args = annotation.__origin__, annotation.__args__

            if issubclass(origin, list):
                return [self.resolve(arg) for arg in args]
            elif issubclass(origin, tuple):
                return tuple(self.resolve(arg) for arg in args)
            elif issubclass(origin, set):
                return {self.resolve(arg) for arg in args}
            elif issubclass(origin, dict):
                key_type, value_type = args
                return {self.resolve(key_type): self.resolve(value_type)}

        elif isinstance(annotation, UnionType):
            args = annotation.__args__
            return self.resolve(choice(args))

        elif annotation is None:
            return None

        raise NotImplementedError(annotation)

    @classmethod
    def _call_provider(cls, provider: PROVIDER_TYPE, annotation: type) -> Any:
        if callable(provider):
            provider: types.FunctionType
            if provider.__code__.co_argcount == 0:
                return provider()
            elif provider.__code__.co_argcount == 1:
                return provider(annotation)
            else:
                raise TypeError(
                    f"Provider for {annotation} should accept 0 or 1 arguments, "
                    f"but it accepts {provider.__code__.co_argcount}"
                )
        else:
            return provider

    def _resolve_for_registered_type(
            self,
            annotation: type,
    ) -> Any:
        for type_, provider in self._providers.items():
            if issubclass(annotation, type_):
                return self._call_provider(provider, annotation)

        if annotation is None or annotation is NoneType:
            return None

    def _resolve_for_pydantic_model(self, model: type[BaseModel]) -> dict[str, Any]:
        # Check for example in model_config
        json_schema_extra = model.model_config.get("json_schema_extra")
        if callable(json_schema_extra):
            json_schema_extra = json_schema_extra()
        if json_schema_extra:
            example: dict | None = json_schema_extra.get("example")
            examples: list[dict] | None = json_schema_extra.get("examples")
            if example is None and examples is not None:
                example = choice(examples)
            if example is not None:
                return example
        example = dict()
        # Iterate over fields
        for field_name, field_info in model.model_fields.items():
            example[field_name] = self._resolve_for_field_info(field_info)
        return example

    def _resolve_for_field_info(self, field_info: FieldInfo):
        if field_info.json_schema_extra and "example" in field_info.json_schema_extra:
            return field_info.json_schema_extra["example"]

        if field_info.examples:
            return choice(field_info.examples)
        elif (
                default := field_info.get_default(call_default_factory=True)
        ) is not PydanticUndefined:
            if default is not None:
                return default
        else:
            rebuilt_annotation = field_info.rebuild_annotation()
            return self.resolve(rebuilt_annotation)
