"""Test suite for import wrappers."""

import re

import pytest

import gymnasium
import gymnasium.wrappers as wrappers
from gymnasium.wrappers import __all__


def test_import_wrappers():
    """Test that all wrappers can be imported."""
    # Test that an invalid wrapper raises an AttributeError
    with pytest.raises(
        AttributeError,
        match=re.escape(
            "module 'gymnasium.wrappers' has no attribute 'NonexistentWrapper'"
        ),
    ):
        getattr(wrappers, "NonexistentWrapper")


@pytest.mark.parametrize("wrapper_name", __all__)
def test_all_wrappers_shortened(wrapper_name):
    """Check that each element of the `__all__` wrappers can be loaded, provided dependencies are installed."""
    try:
        assert getattr(gymnasium.wrappers, wrapper_name) is not None
    except gymnasium.error.DependencyNotInstalled as e:
        pytest.skip(str(e))


def test_wrapper_vector():
    assert gymnasium.wrappers.vector is not None
