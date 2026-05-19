"""Tests unitarios para CameraModule."""

import numpy as np

from src.camera_module import CameraModule


class DummyCapture:
    """Captura simulada para pruebas de cámara."""

    def __init__(self, opened: bool = True, frame=None) -> None:
        self._opened = opened
        self._frame = frame if frame is not None else np.zeros((10, 10, 3))
        self.released = False

    def isOpened(self) -> bool:
        return self._opened

    def read(self):
        return True, self._frame

    def release(self) -> None:
        self.released = True


def test_start_opens_camera(monkeypatch) -> None:
    """Verifica que start() abre la cámara."""
    dummy = DummyCapture(opened=True)
    monkeypatch.setattr("src.camera_module.VIDEO_CAPTURE_CLASS", lambda _: dummy)

    camera = CameraModule()
    camera.start()

    assert camera.is_open() is True


def test_stop_releases_camera(monkeypatch) -> None:
    """Verifica que stop() libera la cámara."""
    dummy = DummyCapture(opened=True)
    monkeypatch.setattr("src.camera_module.VIDEO_CAPTURE_CLASS", lambda _: dummy)

    camera = CameraModule()
    camera.start()
    camera.stop()

    assert dummy.released is True
    assert camera.is_open() is False


def test_read_frame_without_start_returns_none() -> None:
    """Verifica que read_frame() retorna None si no hay cámara abierta."""
    camera = CameraModule()
    assert camera.read_frame() is None


def test_read_frame_returns_frame(monkeypatch) -> None:
    """Verifica que read_frame() retorna un frame cuando la cámara está abierta."""
    frame = np.ones((5, 5, 3))
    dummy = DummyCapture(opened=True, frame=frame)
    monkeypatch.setattr("src.camera_module.VIDEO_CAPTURE_CLASS", lambda _: dummy)

    camera = CameraModule()
    camera.start()

    read = camera.read_frame()
    assert read is not None
    assert read.shape == frame.shape
