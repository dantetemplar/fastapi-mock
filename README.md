# FastAPI Mock

A utility for FastAPI that allows you to create mock endpoints quickly and easily.

## Overview

- [Installation](#installation)
- [Usage](#usage)
    - [Return example instead of `NotImplementedError`](#return-example-instead-of-notimplementederror)
    - [Return example Instead of HTTP 500 Error](#return-example-instead-of-http-500-error)
- [Advanced Usage](#advanced-usage)
    - [Examples in JSON Schema](#examples-in-json-schema)
    - [Field Examples and Defaults](#field-examples-and-defaults)
    - [Custom Provider](#custom-provider)
- [Contributing](#contributing)

## Installation

Install the package using `pip`:

```shell
pip install fastapi-mock
```

> **_NOTE:_** FastAPI Mock requires Python 3.11+ and FastAPI working with Pydantic 2.

## Usage

### Return example instead of `NotImplementedError`

Here, we'll explore how to use `FastAPI Mock` by creating a FastAPI application, adding middleware, and raising
NotImplementedError. Note that we'll be using the MockMiddleware class from the FastAPI Mock.

Let's define our FastAPI application:

```python
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
```

In the above code, we define a FastAPI application, add the `MockMiddleware` to handle the exception, and define a
`GET` endpoint at `/mock-endpoint`. When the endpoint function is called, it raises a `NotImplementedError`
with `ResponseModel` set as the response model and `200` as the status code.

If you hit the endpoint `/mock-endpoint`, you'll see the mock data: just

```json
{
  "message": "Hello, World ❤️"
}
```

> **_NOTE:_** FastAPI Mock can process not only basic types, but `list`, `tuple`, `set`, `dict`, `enum.Enum` generic
> types and `UnionTypo` too. Also, it will resolve response models recursively, so you can define nested models.

### Return example Instead of HTTP 500 Error

It also can replace HTTP 500 error with the example. To enable this feature, just pass
`return_example_instead_of_500=True` to the `MockUtilities` constructor.

```python
from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel

app = FastAPI()

MockUtilities(app, return_example_instead_of_500=True)


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    my_infinity = (
            1 / 0
    )  # raise ZeroDivisionError, then will be converted it to HTTP 500 error
    # in FastAPI ExceptionMiddleware and handled by FastAPI Mock
    return ResponseModel(message=f"UFO is real! and infinity is {my_infinity}")
```

## Advanced Usage

Now we'll look at a more advanced usage of FastAPI Mock, including defining examples in the response model's JSON
schema, utilizing field examples and defaults, configuring middleware with the custom provider
for `int` and `str` types.

### Examples in JSON Schema

FastAPI Mock will choose a random example from the `examples` list in the response model's JSON schema.

Let's try it out:

```python
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
```

The default status code is `200`, so we don't need to
specify it.
Now, if you hit the endpoint `/mock-endpoint`, you'll see the mock data:

```json
{
  "message": "My name is (chka-chka, Slim Shady) - Eminem"
}
```

Or you can define examples in route decorator:

```python
from fastapi import FastAPI
from fastapi_mock import MockUtilities
from pydantic import BaseModel

app = FastAPI()

MockUtilities(app)


class ResponseModel(BaseModel):
    message: str


@app.get(
    "/mock-endpoint",
    openapi_extra={
        "examples": [{"message": "My name is (chka-chka, Slim Shady) - Eminem"}]
    },
)
def mock() -> ResponseModel:
    raise NotImplementedError()
```

> **_PRIORITY:_** The examples from the route decorator have higher priority than the examples from the response model.

### Field Examples and Defaults

FastAPI Mock will iterate through the fields in the response model and choose a random example (or default) from the
field info.

Here's an example:

```python
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
```

Now, if you hit the endpoint `/mock-endpoint`, you'll see the mock data:

```json
{
  "field_with_examples": "Love",
  "field_with_default": "I ❤️ Python",
  "field_with_default_factory": "I ❤️ Python\nI ❤️ Python\nI ❤️ Python\n"
}
```

> **_PRIORITY:_** The examples from the JSON schema have higher priority than the field examples.
> Moreover, the field examples have higher priority than the field defaults.

### Custom Provider

FastAPI Mock uses the constant examples for `str`, random examples for `int` and `float`, `bool` by default.
However, you can configure the middleware to use your own provider for any of basic types.

For example, let's configure the middleware to use the `faker` library for `str` type:

```python
from fastapi import FastAPI
from fastapi_mock import MockUtilities, ExampleProvider
from pydantic import BaseModel
from faker import Faker  # pip install faker

app = FastAPI()
fake = Faker()

MockUtilities(
    app,
    example_provider=ExampleProvider(
        providers={
            str: lambda: fake.sentence()
        }
    )
)


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint")
def mock() -> ResponseModel:
    raise NotImplementedError()
```

Now, if you hit the endpoint `/mock-endpoint`, you'll see the random mock data:

```json
{
  "message": "Some random sentence from faker."
}
```

# Contributing

## Publishing a new version

1. Update the version in `pyproject.toml`
2. Commit the changes
3. Create a new tag with the version number (e.g. `git tag -a 0.1.0 -m "0.1.0"`)
4. Push the tag to the repository (e.g. `git push origin 0.1.0`)
5. Draft a new release on GitHub with the same version number and the release notes
6. Setup poetry PyPi configuration (
   see [tutorial](https://www.digitalocean.com/community/tutorials/how-to-publish-python-packages-to-pypi-using-poetry-on-ubuntu-22-04))
7. Run `poetry build`
8. Run `poetry publish`
9. Attach the built wheel to the release
10. Publish the release
11. Done!

```