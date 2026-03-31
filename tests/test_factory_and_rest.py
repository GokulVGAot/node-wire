from __future__ import annotations

from fastapi.testclient import TestClient

from bindings.factory import ConnectorFactory
from bindings.rest_api.app import app


def test_factory_loads_config():
    factory = ConnectorFactory()
    factory.load()

    http_connector = factory.get_for_protocol("http_generic", "rest")
    assert http_connector is not None

    stripe_rest = factory.get_for_protocol("stripe", "rest")
    assert stripe_rest is None  # stripe not exposed via REST per config


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

