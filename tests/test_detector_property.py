"""Tests de propiedades para Detector."""

from hypothesis import given, settings
from hypothesis import strategies as st
from tempfile import NamedTemporaryFile
import numpy as np

import src.detector as detector_module
from src.detector import Detector
from src.models import VALID_CLASSES


class FakeBox:
    """Caja simulada para pruebas de propiedades."""

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


@given(
    boxes=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=3),
            st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
        ),
        max_size=10,
    )
)
@settings(max_examples=100)
def test_prop_detector_invariants(boxes) -> None:
    # Feature: safestep-uncp, Property 1: Invariante de clases detectadas
    # Feature: safestep-uncp, Property 2: Invariante de umbral de confianza
    with NamedTemporaryFile(suffix=".pt") as tmp_file:
        tmp_file.write(b"fake")
        tmp_file.flush()

        names = {0: "person", 1: "chair", 2: "backpack", 3: "dog"}
        fake_boxes = [
            FakeBox(cls_id, conf, [0, 0, 10, 10]) for cls_id, conf in boxes
        ]
        result = FakeResult(fake_boxes, names)
        fake_model = FakeModel(result)

        previous = detector_module.YOLO_CLASS
        detector_module.YOLO_CLASS = lambda _: fake_model

        try:
            detector = Detector(tmp_file.name, confidence_threshold=0.5)
            detections = detector.detect(np.zeros((10, 10, 3)))

            for det in detections:
                assert det.class_name in VALID_CLASSES
                assert det.confidence >= 0.5
        finally:
            detector_module.YOLO_CLASS = previous
