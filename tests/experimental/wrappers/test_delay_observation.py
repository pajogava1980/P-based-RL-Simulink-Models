"""Test suite for DelayObservationV0."""
import re

import pytest

import gymnasium as gym
from gymnasium.experimental.wrappers import DelayObservationV0
from gymnasium.utils.env_checker import data_equivalence
from gymnasium.vector.utils import create_empty_array
from tests.experimental.wrappers.utils import SEED, complex_testing_env_ids, complex_testing_obs_envs


@pytest.mark.parametrize("env", complex_testing_obs_envs, ids=complex_testing_env_ids)
def test_env_obs(env, delay=3):
    """Tests the delay observation wrapper."""
    env.action_space.seed(SEED)
    env.reset(seed=SEED)

    undelayed_obs = []
    for _ in range(delay + 2):
        obs, _, _, _, _ = env.step(env.action_space.sample())
        undelayed_obs.append(obs)

    env = DelayObservationV0(env, delay=delay)
    env.action_space.seed(SEED)
    env.reset(seed=SEED)

    delayed_obs = []
    for i in range(delay + 2):
        obs, _, _, _, _ = env.step(env.action_space.sample())
        delayed_obs.append(obs)

        if i < delay - 1:
            assert data_equivalence(obs, create_empty_array(env.observation_space))

    assert data_equivalence(delayed_obs[delay:], undelayed_obs[:-delay])


@pytest.mark.parametrize("delay", [1, 2, 3, 4])
def test_delay_values(delay):
    env = gym.make("CartPole-v1")
    first_obs, _ = env.reset(seed=123)

    env = DelayObservationV0(gym.make("CartPole-v1"), delay=delay)
    zero_obs = create_empty_array(env.observation_space)
    obs, _ = env.reset(seed=123)
    assert data_equivalence(obs, zero_obs)
    for _ in range(delay - 1):
        obs, _, _, _, _ = env.step(env.action_space.sample())
        assert data_equivalence(obs, zero_obs)

    obs, _, _, _, _ = env.step(env.action_space.sample())
    assert data_equivalence(first_obs, obs)


def test_delay_failures():
    env = gym.make("CartPole-v1")

    with pytest.raises(TypeError, match=re.escape("The delay is expected to be an integer, actual type: <class 'float'>")):
        DelayObservationV0(env, delay=1.0)

    with pytest.raises(ValueError, match=re.escape("The delay needs to be greater than zero, actual value: -1")):
        DelayObservationV0(env, delay=-1)