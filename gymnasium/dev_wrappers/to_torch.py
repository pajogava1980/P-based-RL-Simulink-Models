# This wrapper will convert torch inputs for the actions and observations to Jax arrays
# for an underlying Jax environment then convert the return observations from Jax arrays
# back to torch tensors.
#
# Functionality for converting between torch and jax types originally copied from
# https://github.com/google/brax/blob/9d6b7ced2a13da0d074b5e9fbd3aad8311e26997/brax/io/torch.py
# Under the Apache 2.0 license. Copyright is held by the authors

"""Helper functions and wrapper class for converting between PyTorch and Jax."""
import functools
from collections import abc
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

from jax._src import dlpack as jax_dlpack
from jax.interpreters.xla import DeviceArray

from gymnasium import Env, Wrapper
from gymnasium.error import DependencyNotInstalled

try:
    import torch
    from torch.utils import dlpack as torch_dlpack
except ImportError:
    raise DependencyNotInstalled("torch is not installed, run `pip install torch`")


Device = Union[str, torch.device]


@functools.singledispatch
def torch_to_jax(value: Any) -> Any:
    """Converts a PyTorch Tensor into a Jax DeviceArray."""
    raise Exception(
        f"No conversion for PyTorch to Jax registered for type: {type(value)}"
    )


@torch_to_jax.register(torch.Tensor)
def _torch_to_jax(value: torch.Tensor) -> DeviceArray:
    """Converts a PyTorch Tensor into a Jax DeviceArray."""
    tensor = torch_dlpack.to_dlpack(value)  # pyright: ignore
    tensor = jax_dlpack.from_dlpack(tensor)
    return tensor


@torch_to_jax.register(abc.Mapping)
def _torch_mapping_to_jax(
    value: Mapping[str, Union[torch.Tensor, Any]]
) -> Mapping[str, Union[DeviceArray, Any]]:
    """Converts a mapping of PyTorch Tensors into a Dictionary of Jax DeviceArrays."""
    return type(value)(**{k: torch_to_jax(v) for k, v in value.items()})


@torch_to_jax.register(abc.Iterable)
def _torch_iterable_to_jax(
    value: Iterable[Union[torch.Tensor, Any]]
) -> Iterable[Union[DeviceArray, Any]]:
    """Converts an Iterable from PyTorch Tensors to an iterable of Jax DeviceArrays."""
    return type(value)(torch_to_jax(v) for v in value)


@functools.singledispatch
def jax_to_torch(value: Any, device: Device = None) -> Any:
    """Converts a Jax DeviceArray into a PyTorch Tensor."""
    raise Exception(
        f"No conversion for Jax to PyTorch registered for type: {type(value)}"
    )


@jax_to_torch.register(DeviceArray)
def _jax_to_torch(value: DeviceArray, device: Device = None) -> torch.Tensor:
    """Converts a Jax DeviceArray into a PyTorch Tensor."""
    dlpack = jax_dlpack.to_dlpack(value.astype("float32"))
    tensor = torch_dlpack.from_dlpack(dlpack)
    if device:
        return tensor.to(device=device)
    else:
        return tensor


@jax_to_torch.register(abc.Mapping)
def _jax_mapping_to_torch(
    value: Mapping[str, Union[DeviceArray, Any]], device: Device = None
) -> Mapping[str, Union[torch.Tensor, Any]]:
    """Converts a mapping of Jax DeviceArrays into a Dictionary of PyTorch Tensors."""
    return type(value)(**{k: jax_to_torch(v, device) for k, v in value.items()})


@jax_to_torch.register(abc.Iterable)
def _jax_iterable_to_torch(
    value: Iterable[Union[torch.Tensor, Any]]
) -> Iterable[Union[DeviceArray, Any]]:
    """Converts an Iterable from Jax DeviceArrays to an iterable of PyTorch Tensors."""
    return type(value)(jax_to_torch(v) for v in value)


class JaxToTorchV0(Wrapper):
    """Wraps an environment so that it can be interacted with through PyTorch Tensors.

    Actions must be provided as PyTorch Tensors and observations will be returned as PyTorch Tensors.

    Note:
        Extensive testing has not been done for handling the device that the Tensor is stored on as
        well as managing the tensor's data type.
    """

    def __init__(self, env: Env, device: Optional[torch.device] = None):
        """Wrapper class to change inputs and outputs of environment to PyTorch tensors.

        Args:
            env: The Jax-based environment to wrap
            device: The device the torch Tensors should be moved to
        """
        super().__init__(env)
        self.device: Optional[torch.device] = device

    def step(
        self, action: torch.Tensor
    ) -> Tuple[Union[torch.Tensor, Dict[str, torch.Tensor]], float, bool, Dict]:
        """Performs the given action within the environment.

        Args:
            action: The action to perform as a PyTorch Tensor

        Returns:
            The next observation, reward, done and extra info
        """
        jax_action = torch_to_jax(action)
        obs, reward, done, info = self.env.step(jax_action)

        obs = jax_to_torch(obs, device=self.device)

        return obs, reward, done, info

    def reset(self, **kwargs) -> Union[torch.Tensor, Tuple[torch.Tensor, Dict]]:
        """Resets the environment."""
        result = self.env.reset(**kwargs)
        if kwargs.get("return_info", False):
            return jax_to_torch(result[0], device=self.device), result[1]
        else:
            return jax_to_torch(result, device=self.device)
