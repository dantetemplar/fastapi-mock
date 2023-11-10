# FastAPI Mock

A middleware for FastAPI that allows you to create mock endpoints quickly and easily.

## Installation

Install the package using `pip`:

```shell
pip install fastapi-mock
```
> **_NOTE:_** FastAPI Mock requires Python 3.11+ and FastAPI working with Pydanctic 2.

## Usage

Here, we'll explore how to use `FastAPI Mock` by creating a FastAPI application, adding middleware, and raising
MockExceptions. Note that we'll be using the MockException and MockMiddleware classes from the FastAPI Mock.

Let's define our FastAPI application:

```python
from fastapi import FastAPI
from fastapi_mock import MockMiddleware, MockException
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(MockMiddleware)  # add middleware as class, not instance


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint")
def mock():
    # instead of ResponseModel, you can use any type annotation that is supported by FastAPI Mock.
    raise MockException(ResponseModel, status_code=200)
```

In the above code, we define a FastAPI application, add the `MockMiddleware` to handle the MockExceptions, and define a
`GET` endpoint at `/mock-endpoint`. When the endpoint function is called, it raises a `MockException`
with `ResponseModel` set as the response model and `200` as the status code.

If you hit the endpoint `/mock-endpoint`, you'll see the mock data: just

```json
{
  "message": "Hello, World ❤️"
}
```


> **_NOTE:_** FastAPI Mock can process not only basic types, but `list`, `tuple`, `set`, `dict`, `enum.Enum` generic 
> types and `UnionTypo` too. Also, it will resolve response models recursively, so you can define nested models.

## Advanced Usage

Now we'll look at a more advanced usage of FastAPI Mock, including defining examples in the response model's JSON
schema, utilizing field examples and defaults, configuring middleware with the custom provider
for `int` and `str` types.

### Examples in JSON Schema

FastAPI Mock will choose a random example from the `examples` list in the response model's JSON schema.

Let's try it out:

```python
from fastapi import FastAPI
from fastapi_mock import MockMiddleware, MockException
from pydantic import BaseModel, ConfigDict

app = FastAPI()

app.add_middleware(MockMiddleware)


class ResponseModel(BaseModel):
    message: str

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "message": "My name is (chka-chka, Slim Shady) - Eminem"
            }
        ]
    })


@app.get("/mock-endpoint")
def mock():
    raise MockException(ResponseModel)
```

The default status code is `200`, so we don't need to
specify it.
Now, if you hit the endpoint `/mock-endpoint`, you'll see the mock data:

```json
{
  "message": "My name is (chka-chka, Slim Shady) - Eminem"
}
``` 

### Field Examples and Defaults

FastAPI Mock will iterate through the fields in the response model and choose a random example (or default) from the
field info.

Here's an example:

```python
from fastapi import FastAPI
from fastapi_mock import MockMiddleware, MockException
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(MockMiddleware)


class ResponseModel(BaseModel):
    field_with_examples: str = Field(examples=["I", "Love", "Python"])
    field_with_default: str = Field(default="I ❤️ Python")
    field_with_default_factory: str = Field(default_factory=lambda: "I ❤️ Python\n" * 3)


@app.get("/mock-endpoint")
def mock():
    raise MockException(ResponseModel)

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
from fastapi_mock import MockMiddleware, MockException, ExampleProvider
from pydantic import BaseModel
from faker import Faker # pip install faker

app = FastAPI()
fake = Faker()

app.add_middleware(
    MockMiddleware, 
    example_provider=ExampleProvider(
        providers={
            str: lambda: fake.sentence()
        }
    )
)


class ResponseModel(BaseModel):
    message: str


@app.get("/mock-endpoint")
def mock():
    raise MockException(ResponseModel)
```

Now, if you hit the endpoint `/mock-endpoint`, you'll see the random mock data:

```json
{
  "message": "Some random sentence."
}
```