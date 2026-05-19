"""Motor de alertas de audio direccionales para SafeStep UNCP."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.models import BoundingBox, Detection


class AlertEngine:
    """Determina dirección del obstáculo y reproduce audio correspondiente."""

    def __init__(self, assets_path: str, sound_loader=None) -> None:
        """Carga los archivos de audio desde el directorio de assets."""
        self._assets_path = Path(assets_path)
        if sound_loader is None:
            from kivy.core.audio import SoundLoader

            sound_loader = SoundLoader

        self._sound_loader = sound_loader
        self._sounds: Dict[str, Optional[object]] = {}
        self._current_alert: Optional[str] = None
        self._load_sounds()

    def _load_sounds(self) -> None:
        """Carga sonidos esperados y reporta los faltantes."""
        sound_files = {
            "left": "alert_left.wav",
            "right": "alert_right.wav",
            "pause": "pause.wav",
            "resume": "resume.wav",
            "no_camera": "no_camera.wav",
            "no_model": "no_model.wav",
        }

        for key, filename in sound_files.items():
            path = self._assets_path / filename
            if not path.exists():
                print(f"Advertencia: falta el archivo de audio {path}", flush=True)
                self._sounds[key] = None
                continue

            sound = self._sound_loader.load(str(path))
            if sound is None:
                print(f"Advertencia: no se pudo cargar el audio {path}", flush=True)
            self._sounds[key] = sound

    def process_detections(self, detections: List[Detection], frame_width: int) -> None:
        """Procesa detecciones, calcula dirección y reproduce alerta."""
        if not detections:
            return

        priority = self.get_priority_detection(detections)
        if priority is None:
            return

        direction = self.classify_direction(priority.bbox, frame_width)
        self.play_alert(direction)

    def get_priority_detection(
        self, detections: List[Detection]
    ) -> Optional[Detection]:
        """Retorna la detección con mayor área de BoundingBox."""
        if not detections:
            return None
        return max(detections, key=lambda det: det.bbox.area)

    def classify_direction(self, bbox: BoundingBox, frame_width: int) -> str:
        """Clasifica la dirección del obstáculo como izquierda o derecha."""
        if frame_width <= 0:
            raise ValueError("El ancho del frame debe ser positivo.")
        return "left" if bbox.center_x < frame_width / 2 else "right"

    def play_alert(self, direction: str) -> None:
        """Reproduce la alerta direccional, evitando duplicados."""
        if direction == self._current_alert and self.is_playing():
            return

        sound = self._sounds.get(direction)
        if sound is None:
            print(f"Advertencia: audio no disponible para '{direction}'", flush=True)
            return

        self._current_alert = direction
        sound.play()

    def play_message(self, message_key: str) -> None:
        """Reproduce un mensaje de audio por clave."""
        sound = self._sounds.get(message_key)
        if sound is None:
            print(
                f"Advertencia: audio no disponible para '{message_key}'",
                flush=True,
            )
            return

        sound.play()

    def is_playing(self) -> bool:
        """Indica si una alerta direccional está en reproducción."""
        if self._current_alert is None:
            return False
        sound = self._sounds.get(self._current_alert)
        return bool(sound is not None and getattr(sound, "state", "") == "play")
