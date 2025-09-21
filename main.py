import os
import yaml
import logging
import argparse

import torch
import numpy as np
from torch.utils.tensorboard import SummaryWriter

import gymnasium as gym
from gymnasium.wrappers import RecordEpisodeStatistics

from utils.logger import configure_logger
from algos.mg_a2c.learning import train_mg_a2c
from algos.rl2_ppo.learning import train_rl2_ppo

from envs.debug.left_right import LeftRightDebugEnv

# from envs.krazy_world.gym_wrapper import initialize_distribution
# KrazyWorld distribution
# envs, test_envs = initialize_distribution(config["max_episode_steps"])


def main(config):
    logging.info(f"Start meta-training, experiment name: {config['name']}")
    logging.info(f"config: {config}")

    envs = [
        RecordEpisodeStatistics(
            LeftRightDebugEnv(max_episode_steps=config["max_episode_steps"])
        ),
        RecordEpisodeStatistics(
            LeftRightDebugEnv(max_episode_steps=config["max_episode_steps"])
        ),
    ]

    test_envs = [
        RecordEpisodeStatistics(
            LeftRightDebugEnv(max_episode_steps=config["max_episode_steps"])
        ),
        RecordEpisodeStatistics(
            LeftRightDebugEnv(max_episode_steps=config["max_episode_steps"])
        ),
    ]

    logging.info(
        f"Env spaces: {envs[0].observation_space, envs[0].action_space}, "
        f"max steps: {config['max_episode_steps']}"
    )

    writer = SummaryWriter(os.path.join(config["path"], "tb"))

    print("Algoritm :", config["algo"])

    if config["algo"] == "rl2_ppo":
        train_rl2_ppo(config, envs, test_envs=test_envs, writer=writer)
    elif config["algo"] == "mg_a2c":
        train_mg_a2c(config, envs, writer=writer)
    else:
        print("No matching Algorithm")


    # Temporary interface to allow all agents to run in similar fashion
    # train_<meta>_<agent>(config, envs: list[Env], test_envs: list[Env], writer)
    # train_mg_a2c(config, envs, writer=writer)
    # train_rl2_ppo(config, envs, test_envs=test_envs, writer=writer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--name",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="run in debug mode",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/rl2_ppo.yml",
    )
    args = parser.parse_args()
    assert args.name is not None, "Pass a name for the experiment"

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Initialize logger
    config["name"] = args.name
    config["debug"] = args.debug
    config["path"] = f"runs/{args.name}"

    # TODO: Refactor Logger to not have to import it everywhere
    configure_logger(args.name, config["path"])

    # CUDA device
    config["device"] = torch.device(config["device_id"])
    torch.autograd.set_detect_anomaly(True)

    # Seed Numpy and Torch
    np.random.seed(config["seed"])
    torch.manual_seed(config["seed"])

    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # print(config["name"])

    main(config)
