"""Módulo de detección de objetos con YOLOv8n."""

from __future__ import annotations

import os
from typing import List

import numpy as np

from src.models import BoundingBox, Detection, VALID_CLASSES

# Permite inyectar un modelo simulado en tests sin importar ultralytics
YOLO_CLASS = None


class Detector:
    """Encapsula la carga del modelo YOLOv8n y la inferencia sobre frames."""

    def __init__(self, model_path: str, confidence_threshold: float = 0.50) -> None:
        """Carga el modelo desde la ruta indicada."""
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")

        global YOLO_CLASS
        if YOLO_CLASS is None:
            from ultralytics import YOLO

            YOLO_CLASS = YOLO

        self._model = YOLO_CLASS(model_path)
        self._confidence_threshold = confidence_threshold
        self._model_loaded = True

    def is_model_loaded(self) -> bool:
        """Retorna True si el modelo fue cargado correctamente."""
        return self._model_loaded

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Ejecuta inferencia sobre un frame y retorna detecciones filtradas."""
        results = self._model.predict(source=frame, verbose=False)
        if not results:
            return []

        result = results[0]
        boxes = result.boxes
        if boxes is None:
            return []

        names = result.names
        detections: List[Detection] = []

        for box in boxes:
            class_id = _to_int(box.cls)
            class_name = names.get(class_id)
            if class_name not in VALID_CLASSES:
                continue

            confidence = _to_float(box.conf)
            if confidence < self._confidence_threshold:
                continue

            coords = _to_list(box.xyxy)
            if len(coords) != 4:
                continue

            bbox = BoundingBox(
                x1=float(coords[0]),
                y1=float(coords[1]),
                x2=float(coords[2]),
                y2=float(coords[3]),
            )
            detections.append(
                Detection(class_name=class_name, confidence=confidence, bbox=bbox)
            )

        return detections


def _to_int(value) -> int:
    """Convierte el valor de clase a entero de forma segura."""
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (list, tuple)) and value:
        value = value[0]
    return int(value)


def _to_float(value) -> float:
    """Convierte la confianza a float."""
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (list, tuple)) and value:
        value = value[0]
    return float(value)


def _to_list(value) -> List[float]:
    """Convierte las coordenadas XYXY a una lista plana de 4 elementos."""
    if isinstance(value, (list, tuple)) and value:
        value = value[0]
    if hasattr(value, "tolist"):
        value = value.tolist()
    coords = list(value)
    if len(coords) == 1 and isinstance(coords[0], (list, tuple)):
        coords = list(coords[0])
    return coords
