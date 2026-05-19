"""Aplicación principal Kivy para SafeStep UNCP."""

from __future__ import annotations

import threading
import time
from queue import Empty, Queue
from typing import List, Optional

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

from src.alert_engine import AlertEngine
from src.camera_module import CameraModule
from src.detector import Detector
from src.models import Detection

# Rutas y configuración principal
MODEL_PATH = "models/yolov8n.pt"
ASSETS_PATH = "assets"
ALERT_URL = "http://198.199.77.68/alert"
CONFIDENCE_THRESHOLD = 0.50
UI_FPS = 15


class CameraWidget(Image):
    """Widget de Kivy que muestra el frame de la cámara en pantalla."""

    def update_frame(self, frame) -> None:
        """Actualiza la textura del widget con un frame BGR de OpenCV."""
        # Import local para evitar dependencias de OpenCV durante tests sin GUI
        import cv2

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame_rgb.shape[:2]

        if self.texture is None or self.texture.size != (width, height):
            self.texture = Texture.create(size=(width, height), colorfmt="rgb")
            self.texture.flip_vertical()

        self.texture.blit_buffer(
            frame_rgb.tobytes(), colorfmt="rgb", bufferfmt="ubyte"
        )
        self.canvas.ask_update()


class SafeStepApp(App):
    """Aplicación Kivy que orquesta cámara, detección y alertas."""

    def __init__(self, **kwargs) -> None:
        """Inicializa el estado interno de la app."""
        super().__init__(**kwargs)
        self._camera: Optional[CameraModule] = None
        self._detector: Optional[Detector] = None
        self._alert_engine: Optional[AlertEngine] = None
        self._is_detecting = True
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._frame_queue: Queue = Queue(maxsize=1)
        self._camera_widget: Optional[CameraWidget] = None
        self._ui_event = None

    def build(self):
        """Construye la UI principal: vista de cámara a pantalla completa."""
        self._camera_widget = CameraWidget()
        self._camera_widget.bind(on_touch_down=self.toggle_detection)
        return self._camera_widget

    def on_start(self) -> None:
        """Inicializa módulos y arranca el pipeline de detección."""
        self._alert_engine = AlertEngine(ASSETS_PATH)
        self._start_pipeline()

    def on_stop(self) -> None:
        """Detiene el pipeline y libera recursos."""
        self._stop_pipeline()

    def on_pause(self) -> bool:
        """Maneja pausa de la app y libera la cámara."""
        self._stop_pipeline()
        return True

    def on_resume(self) -> None:
        """Reanuda la app y reinicia la captura."""
        self._start_pipeline()

    def toggle_detection(self, *_) -> None:
        """Pausa o reanuda la detección cuando el usuario toca la pantalla."""
        self._is_detecting = not self._is_detecting
        if self._alert_engine is None:
            return

        if self._is_detecting:
            self._alert_engine.play_message("resume")
        else:
            self._alert_engine.play_message("pause")

    def _start_pipeline(self) -> None:
        """Configura cámara, detector e inicia el hilo de detección."""
        if self._alert_engine is None:
            self._alert_engine = AlertEngine(ASSETS_PATH)

        self._camera = CameraModule()
        self._camera.start()
        if not self._camera.is_open():
            self._alert_engine.play_message("no_camera")
            return

        try:
            self._detector = Detector(
                model_path=MODEL_PATH, confidence_threshold=CONFIDENCE_THRESHOLD
            )
        except FileNotFoundError:
            self._alert_engine.play_message("no_model")
            return

        self._is_detecting = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._detection_loop, daemon=True)
        self._thread.start()

        self._ui_event = Clock.schedule_interval(self._update_ui, 1 / UI_FPS)

    def _stop_pipeline(self) -> None:
        """Detiene el hilo de detección y libera la cámara."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

        if self._camera is not None:
            self._camera.stop()
            self._camera = None

        if self._ui_event is not None:
            self._ui_event.cancel()
            self._ui_event = None

    def _detection_loop(self) -> None:
        """Bucle principal de detección ejecutado en hilo de fondo."""
        while not self._stop_event.is_set():
            if self._camera is None or self._detector is None:
                time.sleep(0.05)
                continue

            frame = self._camera.read_frame()
            if frame is None:
                continue

            self._enqueue_frame(frame)

            if self._is_detecting:
                detections = self._detector.detect(frame)
                if detections and self._alert_engine is not None:
                    self._alert_engine.process_detections(
                        detections, frame_width=frame.shape[1]
                    )
                    self._send_detection_post(detections)

            time.sleep(0.001)

    def _enqueue_frame(self, frame) -> None:
        """Guarda el frame más reciente para la UI."""
        if self._frame_queue.full():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                pass
        self._frame_queue.put_nowait(frame)

    def _update_ui(self, _dt) -> None:
        """Actualiza la vista de cámara desde el hilo principal."""
        if self._camera_widget is None:
            return

        try:
            frame = self._frame_queue.get_nowait()
        except Empty:
            return

        self._camera_widget.update_frame(frame)

    def _send_detection_post(self, detections: List[Detection]) -> None:
        """Envía un POST HTTP con las clases detectadas."""
        clases = sorted({det.class_name for det in detections})
        payload = {"evento": "deteccion", "clases": clases}
        try:
            requests.post(ALERT_URL, json=payload, timeout=3)
        except requests.RequestException as exc:
            print(f"Error al enviar POST: {exc}", flush=True)


if __name__ == "__main__":
    # Punto de entrada principal
    SafeStepApp().run()
