"""Module of wrapper classes."""
from gymnasium import error
from gymnasium.dev_wrappers.lambda_action import LambdaActionV0
from gymnasium.dev_wrappers.lambda_observations import LambdaObservationsV0
from gymnasium.dev_wrappers.lambda_reward import ClipRewardsV0, LambdaRewardV0
from gymnasium.wrappers.atari_preprocessing import AtariPreprocessing
from gymnasium.wrappers.autoreset import AutoResetWrapper
from gymnasium.wrappers.clip_action import ClipAction
from gymnasium.wrappers.filter_observation import FilterObservation
from gymnasium.wrappers.flatten_observation import FlattenObservation
from gymnasium.wrappers.frame_stack import FrameStack, LazyFrames
from gymnasium.wrappers.gray_scale_observation import GrayScaleObservation
from gymnasium.wrappers.human_rendering import HumanRendering
from gymnasium.wrappers.normalize import NormalizeObservation, NormalizeReward
from gymnasium.wrappers.order_enforcing import OrderEnforcing
from gymnasium.wrappers.record_episode_statistics import RecordEpisodeStatistics
from gymnasium.wrappers.record_video import RecordVideo, capped_cubic_video_schedule
from gymnasium.wrappers.render_collection import RenderCollection
from gymnasium.wrappers.rescale_action import RescaleAction
from gymnasium.wrappers.resize_observation import ResizeObservation
from gymnasium.wrappers.step_api_compatibility import StepAPICompatibility
from gymnasium.wrappers.time_aware_observation import TimeAwareObservation
from gymnasium.wrappers.time_limit import TimeLimit
from gymnasium.wrappers.transform_observation import TransformObservation
from gymnasium.wrappers.transform_reward import TransformReward
from gymnasium.wrappers.vector_list_info import VectorListInfo
