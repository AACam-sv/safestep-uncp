"""Test de integración ligero del envío de detecciones."""

from src import main
from src.models import BoundingBox, Detection


def test_send_detection_post(monkeypatch) -> None:
    """Verifica que el POST incluya clases detectadas."""
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout

        class DummyResponse:
            status_code = 200

        return DummyResponse()

    monkeypatch.setattr(main.requests, "post", fake_post)

    app = main.SafeStepApp()
    detections = [
        Detection("person", 0.9, BoundingBox(0, 0, 10, 10)),
        Detection("chair", 0.9, BoundingBox(0, 0, 10, 10)),
    ]

    app._send_detection_post(detections)

    assert captured["url"] == main.ALERT_URL
    assert set(captured["json"]["clases"]) == {"person", "chair"}
