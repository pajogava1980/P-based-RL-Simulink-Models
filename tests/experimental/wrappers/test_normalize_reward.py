"""Test suite for NormalizeRewardV0."""
import numpy as np

from gymnasium.core import ActType
from gymnasium.experimental.wrappers import NormalizeRewardV0
from gymnasium.vector import SyncVectorEnv
from tests.testing_env import GenericTestEnv


def _make_reward_env():
    """Functions that returns an `GenericTestEnv` with reward=1."""

    def step_func(self, action: ActType):
        return self.observation_space.sample(), 1.0, False, False, {}

    return GenericTestEnv(step_func=step_func)


def test_normalize_reward_wrapper():
    """Tests that the NormalizeReward does not throw an error."""
    # TODO: Functional correctness should be tested
    env = _make_reward_env()
    wrapped_env = NormalizeRewardV0(env)
    wrapped_env.reset()
    _, reward, _, _, _ = wrapped_env.step(None)
    assert np.ndim(reward) == 0
    env.close()


def test_vec_normalize_reward_wrapper():
    """Tests that the NormalizeReward does not throw an error for VectorEnv."""
    # TODO: Functional correctness should be tested
    envs = SyncVectorEnv([_make_reward_env, _make_reward_env])
    wrapped_env = NormalizeRewardV0(envs)
    wrapped_env.reset()
    _, reward, _, _, _ = wrapped_env.step([None, None])
    assert np.ndim(reward) > 0
    envs.close
