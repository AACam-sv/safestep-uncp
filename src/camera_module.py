"""Módulo de cámara basado en OpenCV para SafeStep UNCP."""

from typing import Optional, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import cv2

# Permite inyectar un capturador simulado en tests sin importar OpenCV
VIDEO_CAPTURE_CLASS = None


class CameraModule:
    """Gestiona la captura de video desde la cámara del dispositivo."""

    def __init__(self, camera_index: int = 0) -> None:
        """Inicializa el módulo con el índice de cámara a utilizar."""
        self._camera_index = camera_index
        self._cap: Optional[object] = None
        self._is_running = False

    def start(self) -> None:
        """Abre la cámara y comienza la captura."""
        if self._is_running:
            return

        global VIDEO_CAPTURE_CLASS
        if VIDEO_CAPTURE_CLASS is None:
            import cv2

            VIDEO_CAPTURE_CLASS = cv2.VideoCapture

        self._cap = VIDEO_CAPTURE_CLASS(self._camera_index)
        if self._cap is None or not self._cap.isOpened():
            self._is_running = False
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            return

        self._is_running = True

    def stop(self) -> None:
        """Libera el recurso de la cámara y detiene la captura."""
        if self._cap is not None:
            self._cap.release()
        self._cap = None
        self._is_running = False

    def read_frame(self) -> Optional[np.ndarray]:
        """Captura un frame BGR y lo retorna; None si falla la lectura."""
        if not self._is_running or self._cap is None:
            return None

        ok, frame = self._cap.read()
        if not ok:
            return None

        return frame

    def is_open(self) -> bool:
        """Indica si la cámara está abierta y lista para capturar."""
        return bool(self._is_running and self._cap is not None and self._cap.isOpened())
