"""Modelos de datos para detecciones de SafeStep UNCP."""

from dataclasses import dataclass

# Conjunto de clases objetivo reconocidas por el sistema
VALID_CLASSES = {"person", "chair", "backpack"}


@dataclass
class BoundingBox:
    """Representa un rectángulo delimitador en coordenadas de píxeles."""

    x1: float
    """Coordenada X del borde izquierdo."""

    y1: float
    """Coordenada Y del borde superior."""

    x2: float
    """Coordenada X del borde derecho."""

    y2: float
    """Coordenada Y del borde inferior."""

    @property
    def center_x(self) -> float:
        """Retorna la coordenada X del centro del rectángulo."""
        return (self.x1 + self.x2) / 2

    @property
    def area(self) -> float:
        """Retorna el área del rectángulo delimitador."""
        return (self.x2 - self.x1) * (self.y2 - self.y1)


@dataclass
class Detection:
    """Representa una detección de objeto con clase, confianza y bounding box."""

    class_name: str
    """Nombre de la clase detectada."""

    confidence: float
    """Nivel de confianza de la detección (0.0 - 1.0)."""

    bbox: BoundingBox
    """Rectángulo delimitador asociado a la detección."""
