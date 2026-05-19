"""Tests unitarios para Detector."""

from pathlib import Path

import numpy as np

from src.detector import Detector
from src.models import VALID_CLASSES


class FakeBox:
    """Caja simulada para pruebas de detección."""

    def __init__(self, cls_id: int, conf: float, xyxy):
        self.cls = np.array([cls_id])
        self.conf = np.array([conf])
        self.xyxy = np.array([xyxy])


class FakeResult:
    """Resultado simulado de YOLO."""

    def __init__(self, boxes, names):
        self.boxes = boxes
        self.names = names


class FakeModel:
    """Modelo simulado con respuesta controlada."""

    def __init__(self, result):
        self._result = result

    def predict(self, source, verbose=False):
        return [self._result]


def test_detector_filters_by_confidence(tmp_path, monkeypatch) -> None:
    """Verifica que se filtra por umbral de confianza."""
    model_path = tmp_path / "model.pt"
    model_path.write_text("fake")

    names = {0: "person"}
    boxes = [FakeBox(0, 0.4, [0, 0, 10, 10]), FakeBox(0, 0.8, [0, 0, 10, 10])]
    result = FakeResult(boxes, names)
    fake_model = FakeModel(result)

    monkeypatch.setattr("src.detector.YOLO_CLASS", lambda _: fake_model)

    detector = Detector(str(model_path), confidence_threshold=0.5)
    detections = detector.detect(np.zeros((10, 10, 3)))

    assert len(detections) == 1
    assert detections[0].confidence >= 0.5


def test_detector_filters_by_class(tmp_path, monkeypatch) -> None:
    """Verifica que solo retorna clases válidas."""
    model_path = tmp_path / "model.pt"
    model_path.write_text("fake")

    names = {0: "person", 1: "dog"}
    boxes = [FakeBox(0, 0.9, [0, 0, 10, 10]), FakeBox(1, 0.9, [0, 0, 10, 10])]
    result = FakeResult(boxes, names)
    fake_model = FakeModel(result)

    monkeypatch.setattr("src.detector.YOLO_CLASS", lambda _: fake_model)

    detector = Detector(str(model_path))
    detections = detector.detect(np.zeros((10, 10, 3)))

    assert len(detections) == 1
    assert detections[0].class_name in VALID_CLASSES


def test_detector_returns_empty_when_no_boxes(tmp_path, monkeypatch) -> None:
    """Verifica que detect() retorna lista vacía si no hay boxes."""
    model_path = tmp_path / "model.pt"
    model_path.write_text("fake")

    result = FakeResult(boxes=None, names={})
    fake_model = FakeModel(result)

    monkeypatch.setattr("src.detector.YOLO_CLASS", lambda _: fake_model)

    detector = Detector(str(model_path))
    detections = detector.detect(np.zeros((10, 10, 3)))

    assert detections == []
