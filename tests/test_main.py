"""Tests unitarios para la app principal."""

from src import main


class FakeAlertEngine:
    """Motor de alertas simulado."""

    def __init__(self, *_args, **_kwargs) -> None:
        self.messages = []

    def play_message(self, key: str) -> None:
        self.messages.append(key)


class FakeCameraModule:
    """Cámara simulada con estado controlado."""

    def __init__(self, *_args, **_kwargs) -> None:
        self._open = False

    def start(self) -> None:
        self._open = False

    def is_open(self) -> bool:
        return self._open

    def stop(self) -> None:
        self._open = False


class FakeDetector:
    """Detector simulado que fuerza error de modelo."""

    def __init__(self, *_args, **_kwargs) -> None:
        raise FileNotFoundError("modelo no encontrado")


def test_on_start_no_camera(monkeypatch) -> None:
    """Verifica que se reproduzca no_camera si la cámara falla."""
    monkeypatch.setattr(main, "AlertEngine", FakeAlertEngine)
    monkeypatch.setattr(main, "CameraModule", FakeCameraModule)

    app = main.SafeStepApp()
    app.on_start()

    assert app._alert_engine is not None
    assert "no_camera" in app._alert_engine.messages


def test_on_start_no_model(monkeypatch) -> None:
    """Verifica que se reproduzca no_model si falta el modelo."""
    class CameraOk(FakeCameraModule):
        def start(self) -> None:
            self._open = True

        def is_open(self) -> bool:
            return True

    monkeypatch.setattr(main, "AlertEngine", FakeAlertEngine)
    monkeypatch.setattr(main, "CameraModule", CameraOk)
    monkeypatch.setattr(main, "Detector", FakeDetector)

    app = main.SafeStepApp()
    app.on_start()

    assert app._alert_engine is not None
    assert "no_model" in app._alert_engine.messages


def test_toggle_detection_changes_state(monkeypatch) -> None:
    """Verifica el cambio de estado al tocar la pantalla."""
    monkeypatch.setattr(main, "AlertEngine", FakeAlertEngine)
    app = main.SafeStepApp()
    app._alert_engine = FakeAlertEngine()
    app._is_detecting = True

    app.toggle_detection()
    assert app._is_detecting is False
    assert "pause" in app._alert_engine.messages

    app.toggle_detection()
    assert app._is_detecting is True
    assert "resume" in app._alert_engine.messages
