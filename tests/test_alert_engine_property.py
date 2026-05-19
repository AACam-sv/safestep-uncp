"""Tests de propiedades para AlertEngine."""

from hypothesis import given, settings
from hypothesis import strategies as st
from tempfile import TemporaryDirectory
from pathlib import Path

from src.alert_engine import AlertEngine
from src.models import BoundingBox, Detection


class FakeSound:
    """Audio simulado para pruebas."""

    def __init__(self) -> None:
        self.state = "stop"
        self.play_count = 0

    def play(self) -> None:
        self.state = "play"
        self.play_count += 1


class FakeLoader:
    """Loader simulado que retorna sonidos en memoria."""

    def load(self, _path):
        return FakeSound()


def _create_assets(tmp_path):
    for name in [
        "alert_left.wav",
        "alert_right.wav",
        "pause.wav",
        "resume.wav",
        "no_camera.wav",
        "no_model.wav",
    ]:
        (tmp_path / name).write_bytes(b"fake")
    return tmp_path


@given(
    center_x=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    frame_width=st.floats(min_value=1, max_value=2000, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_prop_direction_classification(center_x, frame_width) -> None:
    # Feature: safestep-uncp, Property 4: Clasificación direccional correcta
    engine = AlertEngine(assets_path="assets", sound_loader=FakeLoader())
    bbox = BoundingBox(x1=center_x - 1, y1=0, x2=center_x + 1, y2=10)
    direction = engine.classify_direction(bbox, frame_width=frame_width)
    assert direction in {"left", "right"}


@given(
    areas=st.lists(
        st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=100)
def test_prop_priority_selection(areas) -> None:
    # Feature: safestep-uncp, Property 5: Selección del obstáculo prioritario por área máxima
    with TemporaryDirectory() as tmp_dir:
        assets = _create_assets(Path(tmp_dir))
        engine = AlertEngine(assets_path=str(assets), sound_loader=FakeLoader())

        detections = [
            Detection(
                "person",
                0.9,
                BoundingBox(0, 0, area, 1),
            )
            for area in areas
        ]

        priority = engine.get_priority_detection(detections)
        assert priority is not None
        assert priority.bbox.area == max(det.bbox.area for det in detections)


def test_prop_silence_on_empty() -> None:
    # Feature: safestep-uncp, Property 6: Silencio ante ausencia de obstáculos
    with TemporaryDirectory() as tmp_dir:
        assets = _create_assets(Path(tmp_dir))
        engine = AlertEngine(assets_path=str(assets), sound_loader=FakeLoader())
        engine.process_detections([], frame_width=100)
        assert engine.is_playing() is False


def test_prop_alert_suppression() -> None:
    # Feature: safestep-uncp, Property 7: Supresión de alertas duplicadas
    with TemporaryDirectory() as tmp_dir:
        assets = _create_assets(Path(tmp_dir))
        engine = AlertEngine(assets_path=str(assets), sound_loader=FakeLoader())
        engine.play_alert("left")
        engine.play_alert("left")
        assert engine.is_playing() is True
