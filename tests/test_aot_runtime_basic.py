from __future__ import annotations

import asyncio

from pydantic import BaseModel

from runtime import BaseConnector, ConnectorResponse, ErrorCategory, ErrorMapper


class InputModel(BaseModel):
    value: int


class OutputModel(BaseModel):
    doubled: int


class TestConnector(BaseConnector[InputModel, OutputModel]):
    connector_id = "test"
    action = "double"

    async def internal_execute(self, params: InputModel, *, trace_id: str) -> OutputModel:
        return OutputModel(doubled=params.value * 2)


def test_successful_execution():
    connector = TestConnector(InputModel, OutputModel)

    response: ConnectorResponse = asyncio.run(connector.run({"value": 2}))

    assert response.success is True
    assert response.data == {"doubled": 4}
    assert response.error_code is None
    assert response.error_category is None
    assert isinstance(response.trace_id, str)


class CustomError(Exception):
    pass


class FailingConnector(BaseConnector[InputModel, OutputModel]):
    connector_id = "test"
    action = "fail"

    async def internal_execute(self, params: InputModel, *, trace_id: str) -> OutputModel:
        raise CustomError("boom")


def test_error_mapping_defaults_to_fatal():
    connector = FailingConnector(InputModel, OutputModel)

    response: ConnectorResponse = asyncio.run(connector.run({"value": 1}))

    assert response.success is False
    assert response.error_code == "CustomError"
    assert response.error_category == ErrorCategory.FATAL


def test_error_mapping_custom_category():
    ErrorMapper.register(CustomError, ErrorCategory.RETRYABLE, code="CUSTOM_RETRYABLE")
    connector = FailingConnector(InputModel, OutputModel)

    response: ConnectorResponse = asyncio.run(connector.run({"value": 1}))

    assert response.success is False
    assert response.error_code == "CUSTOM_RETRYABLE"
    assert response.error_category == ErrorCategory.RETRYABLE

