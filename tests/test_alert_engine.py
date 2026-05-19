"""Tests unitarios para AlertEngine."""

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

    def __init__(self) -> None:
        self.sounds = {}

    def load(self, _path):
        sound = FakeSound()
        self.sounds[_path] = sound
        return sound


def _create_assets(tmp_path: Path) -> Path:
    """Crea archivos vacíos de audio para pruebas."""
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


def test_classify_direction() -> None:
    """Verifica la clasificación izquierda/derecha."""
    engine = AlertEngine(assets_path="assets", sound_loader=FakeLoader())
    bbox_left = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    bbox_right = BoundingBox(x1=60, y1=0, x2=100, y2=10)

    assert engine.classify_direction(bbox_left, frame_width=200) == "left"
    assert engine.classify_direction(bbox_right, frame_width=100) == "right"


def test_get_priority_detection(tmp_path) -> None:
    """Verifica que se seleccione la detección con mayor área."""
    assets = _create_assets(tmp_path)
    engine = AlertEngine(assets_path=str(assets), sound_loader=FakeLoader())

    det_small = Detection("person", 0.9, BoundingBox(0, 0, 10, 10))
    det_large = Detection("chair", 0.9, BoundingBox(0, 0, 20, 20))

    priority = engine.get_priority_detection([det_small, det_large])
    assert priority == det_large


def test_process_detections_empty_does_not_play(tmp_path) -> None:
    """Verifica que con lista vacía no se reproduce audio."""
    assets = _create_assets(tmp_path)
    loader = FakeLoader()
    engine = AlertEngine(assets_path=str(assets), sound_loader=loader)

    engine.process_detections([], frame_width=100)

    assert all(sound.play_count == 0 for sound in loader.sounds.values())


def test_play_alert_suppresses_duplicates(tmp_path) -> None:
    """Verifica la supresión de alertas duplicadas."""
    assets = _create_assets(tmp_path)
    loader = FakeLoader()
    engine = AlertEngine(assets_path=str(assets), sound_loader=loader)

    engine.play_alert("left")
    engine.play_alert("left")

    sounds = list(loader.sounds.values())
    assert sounds[0].play_count == 1
