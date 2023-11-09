__all__ = ["resolve"]

from enum import Enum
from random import choice
from types import NoneType, GenericAlias, UnionType
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from fastapi_mock.example_provider import ExampleProvider


def resolve(annotation: type[Any] | None, example_provider: ExampleProvider) -> Any:
    if isinstance(annotation, type):
        if issubclass(annotation, (int, float, str, bool, NoneType)):
            return _resolve_for_basic_type(annotation, example_provider)
        elif issubclass(annotation, BaseModel):
            return _resolve_for_pydantic_model(annotation, example_provider)
        elif issubclass(annotation, Enum):
            return _resolve_for_enum(annotation)

    elif isinstance(annotation, GenericAlias):
        origin, args = annotation.__origin__, annotation.__args__

        if issubclass(origin, list):
            return [resolve(arg, example_provider) for arg in args]
        elif issubclass(origin, tuple):
            return tuple(resolve(arg, example_provider) for arg in args)
        elif issubclass(origin, dict):
            key_type, value_type = args
            return {
                resolve(key_type, example_provider): resolve(
                    value_type, example_provider
                )
            }

    elif isinstance(annotation, UnionType):
        args = annotation.__args__
        return resolve(choice(args), example_provider)

    elif annotation is None:
        return None

    raise NotImplementedError(annotation)


def _resolve_for_basic_type(
    annotation: type[int | float | str | bool] | NoneType,
    example_provider: ExampleProvider,
) -> Any:
    if issubclass(annotation, int):
        return example_provider.INT.get_default(call_default_factory=True)
    elif issubclass(annotation, float):
        return example_provider.FLOAT.get_default(call_default_factory=True)
    elif issubclass(annotation, str):
        return example_provider.STR.get_default(call_default_factory=True)
    elif issubclass(annotation, bool):
        return example_provider.BOOL.get_default(call_default_factory=True)
    elif annotation is NoneType:
        return None


def _resolve_for_pydantic_model(
    model: type[BaseModel], example_provider: ExampleProvider
) -> dict[str, Any]:
    # Check for example in model_config
    json_schema_extra = model.model_config.get("json_schema_extra")
    if json_schema_extra:
        example: dict | None = json_schema_extra.get("example")
        if example:
            return example
    example = dict()
    # Iterate over fields
    for field_name, field_info in model.model_fields.items():
        example[field_name] = _resolve_for_field_info(field_info, example_provider)
    return example


def _resolve_for_field_info(field_info: FieldInfo, example_provider: ExampleProvider):
    if field_info.examples:
        return choice(field_info.examples)
    elif (
        default := field_info.get_default(call_default_factory=True)
    ) is not PydanticUndefined:
        if default is not None:
            return default
    else:
        rebuilt_annotation = field_info.rebuild_annotation()
        return resolve(rebuilt_annotation, example_provider)


def _resolve_for_enum(enumeration: type[Enum]) -> Any:
    return choice(list(enumeration.__members__.values()))
