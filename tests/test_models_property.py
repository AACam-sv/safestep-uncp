"""Tests basados en propiedades para modelos de datos."""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.models import BoundingBox


@given(
    x1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    y1=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    width=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
    height=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_prop_bbox_structure(x1, y1, width, height) -> None:
    # Feature: safestep-uncp, Property 3: Estructura válida de detecciones
    # Feature: safestep-uncp, Property 9: Invariante de BoundingBox válido
    x2 = x1 + width
    y2 = y1 + height

    bbox = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
    assert bbox.center_x == (x1 + x2) / 2
    assert bbox.area > 0
