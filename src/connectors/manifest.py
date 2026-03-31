from __future__ import annotations

from typing import Any, Dict, List, Type

from pydantic import BaseModel

from runtime import BaseConnector


def _schema_for(model: Type[BaseModel]) -> Dict[str, Any]:
    return model.model_json_schema()


def build_manifest(connectors: List[BaseConnector[Any, Any]]) -> List[Dict[str, Any]]:
    """
    Build a simple manifest for discovery.

    Each entry describes a connector/action pair and includes JSON Schemas
    for the input and output models. This is consumed by Layer C for
    REST route generation and MCP tool manifests.
    """
    manifest: List[Dict[str, Any]] = []
    for connector in connectors:
        input_model = connector._input_model_cls  # type: ignore[attr-defined]
        output_model = connector._output_model_cls  # type: ignore[attr-defined]
        manifest.append(
            {
                "connector_id": connector.connector_id,
                "action": connector.action,
                "input_schema": _schema_for(input_model),
                "output_schema": _schema_for(output_model),
            }
        )
    return manifest

