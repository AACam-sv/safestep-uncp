"""Tests de propiedad para el toggle de detección."""

from hypothesis import given, settings
from hypothesis import strategies as st

from src import main


class FakeAlertEngine:
    """Motor de alertas simulado para el test."""

    def play_message(self, _key: str) -> None:
        return None


@given(initial_state=st.booleans())
@settings(max_examples=100)
def test_prop_toggle_roundtrip(initial_state) -> None:
    # Feature: safestep-uncp, Property 8: Toggle de detección (round-trip)
    app = main.SafeStepApp()
    app._alert_engine = FakeAlertEngine()
    app._is_detecting = initial_state

    app.toggle_detection()
    app.toggle_detection()

    assert app._is_detecting == initial_state
