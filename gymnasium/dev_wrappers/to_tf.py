"""Helper functions and wrapper class for converting between TensorFlow and Jax."""
import functools
import numbers
from collections import abc
from typing import Any, Dict, Iterable, Mapping, Tuple, Union

import jax.numpy as jnp
from jax._src import dlpack as jax_dlpack
from jax.interpreters.xla import DeviceArray

from gymnasium import Env, Wrapper
from gymnasium.error import DependencyNotInstalled

try:
    import tensorflow as tf
except ImportError:
    raise DependencyNotInstalled(
        "tensorflow is not installed, run `pip install tensorflow`"
    )


@functools.singledispatch
def tf_to_jax(value: Any) -> Any:
    """Converts values to Jax tensors."""
    raise Exception(
        f"No conversion for TensorFlow to Jax registered for type: {type(value)}"
    )


@tf_to_jax.register(tf.Tensor)
def _tf_to_jax(value: tf.Tensor) -> DeviceArray:
    """Converts a TensorFlow Tensor to a Jax DeviceArray."""
    return jax_dlpack.from_dlpack(tf.experimental.dlpack.to_dlpack(value))


@tf_to_jax.register(numbers.Number)
def _tf_number_to_jax(value: numbers.Number) -> DeviceArray:
    """Converts a number to a Jax DeviceArray."""
    return jnp.array(value)


@tf_to_jax.register(abc.Mapping)
def _tf_mapping_to_jax(
    value: Mapping[str, Union[tf.Tensor, Any]]
) -> Mapping[str, Union[DeviceArray, Any]]:
    """Converts a dictionary of TensorFlow Tensors to a mapping of Jax DeviceArrays."""
    return type(value)(**{k: tf_to_jax(v) for k, v in value.items()})


@tf_to_jax.register(abc.Iterable)
def _tf_iterable_to_jax(
    value: Iterable[Union[tf.Tensor, Any]]
) -> Iterable[Union[DeviceArray, Any]]:
    """Converts an Iterable from TensorFlow Tensors to an iterable of Jax DeviceArrays."""
    return type(value)(tf_to_jax(v) for v in value)


@functools.singledispatch
def jax_to_tf(value: Any) -> Any:
    """Converts a value to a TensorFlow tensor."""
    raise Exception(
        f"No conversion for Jax to TensorFlow registered for type: {type(value)}"
    )


@jax_to_tf.register(DeviceArray)
def _jax_to_tf(value: DeviceArray) -> tf.Tensor:
    """Converts a Jax DeviceArray to a TensorFlow tensor."""
    return tf.experimental.dlpack.from_dlpack(jax_dlpack.to_dlpack(value))


@jax_to_tf.register(abc.Mapping)
def _jax_mapping_to_tf(
    value: Mapping[str, Union[DeviceArray, Any]]
) -> Mapping[str, Union[tf.Tensor, Any]]:
    """Converts a mapping of Jax DeviceArrays to TensorFlow tensors."""
    return type(value)(**{k: jax_to_tf(v) for k, v in value.items()})


@jax_to_tf.register(abc.Iterable)
def _jax_iterable_to_tf(
    value: Iterable[Union[DeviceArray, Any]]
) -> Iterable[Union[tf.Tensor, Any]]:
    """Converts an Iterable from Jax DeviceArrays to an iterable of TensorFlow Tensors."""
    return type(value)([jax_to_tf(v) for v in value])


class JaxToTFV0(Wrapper):
    """Wraps an environment so that it can be interacted with through TensorFlow Tensors.

    Actions must be provided as TensorFlow Tensors and observations will be returned as TensorFlow Tensors.

    Note:
        Extensive testing has not been done for handling the tensor's data type.
    """

    def __init__(self, env: Env):
        """Wraps an environment so that the input and outputs are TensorFlow tensors.

        Args:
            env: The Jax-based environment to wrap
        """
        super().__init__(env)

    def step(self, action: tf.Tensor):
        """Performs the given action in the environment.

        Args:
            action: the action to perform as a TensorFlow Tensor

        Returns:
            A tuple containing the next observation, reward, done, and extra info
        """
        jax_action = tf_to_jax(action)
        obs, reward, done, info = self.env.step(jax_action)

        obs = jax_to_tf(obs)

        return obs, reward, done, info

    def reset(self, **kwargs) -> Union[tf.Tensor, Tuple[tf.Tensor, dict]]:
        """Resets the environment."""
        result = self.env.reset(**kwargs)
        if kwargs.get("return_info", False):
            return jax_to_tf(result[0]), result[1]
        else:
            return jax_to_tf(result)
