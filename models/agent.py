#
# Wheatley
# Copyright (c) 2023 Jolibrain
# Authors:
#    Guillaume Infantes <guillaume.infantes@jolibrain.com>
#    Antoine Jacquet <antoine.jacquet@jolibrain.com>
#    Michel Thomazo <thomazo.michel@gmail.com>
#    Emmanuel Benazera <emmanuel.benazera@jolibrain.com>
#
#
# This file is part of Wheatley.
#
# Wheatley is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wheatley is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wheatley. If not, see <https://www.gnu.org/licenses/>.
#

import pickle

from stable_baselines3.common.callbacks import EveryNTimesteps
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines3.ppo import PPO
from stable_baselines3.a2c import A2C

# from sb3_contrib.ppo_mask import MaskablePPO
from models.maskable_ppo_custom import MaskablePPOCustom

from sb3_contrib.common.maskable.utils import get_action_masks
import torch

from env.env import Env
from models.agent_callback import ValidationCallback
from models.policy import Policy, RPOPolicy
from models.features_extractor_dgl import FeaturesExtractorDGL
from models.features_extractor_tokengt import FeaturesExtractorTokenGT
from problem.problem_description import ProblemDescription
from utils.utils import lr_schedule_linear

from functools import partial


def make_proc_env(problem_description, env_specification):
    def _init():
        env = Env(problem_description, env_specification)
        return env

    return _init


class Agent:
    def __init__(
        self,
        env_specification,
        model=None,
        agent_specification=None,
    ):
        """
        There are 2 ways to init an Agent:
         - Either provide a valid env_specification and agent_specification
         - Or use the load method, to load an already saved Agent
        """
        self.env_specification = env_specification

        # User must provide an agent_specification or a model at least.
        if agent_specification is None and model is None:
            raise Exception("Please provide an agent_specification or a model to create a new Agent")

        # If a model is provided, we simply load the existing model.
        if model is not None:
            self.model = model
            return

        # Else, we have to build a new PPO instance.
        self.model = None
        self.n_workers = agent_specification.n_workers
        self.device = agent_specification.device
        self.agent_specification = agent_specification

    def save(self, path):
        """Saving an agent corresponds to saving his model and a few args to specify how the model is working"""
        self.model.save(path)
        with open(path + ".pickle", "wb") as f:
            pickle.dump({"env_specification": self.env_specification, "n_workers": self.n_workers, "device": self.device}, f)

    @classmethod
    def load(cls, path):
        """Loading an agent corresponds to loading his model and a few args to specify how the model is working"""
        with open(path + ".pickle", "rb") as f:
            kwargs = pickle.load(f)
        agent = cls(env_specification=kwargs["env_specification"], model=MaskablePPOCustom.load(path))
        agent.n_workers = kwargs["n_workers"]
        agent.device = kwargs["device"]
        return agent

    def train(
        self,
        problem_description,
        training_specification,
    ):
        # First setup callbacks during training
        validation_callback = ValidationCallback(
            problem_description=problem_description,
            env_specification=self.env_specification,
            n_workers=self.n_workers,
            device=self.device,
            n_validation_env=training_specification.n_validation_env,
            fixed_validation=training_specification.fixed_validation,
            fixed_random_validation=training_specification.fixed_random_validation,
            validation_batch_size=training_specification.validation_batch_size,
            display_env=training_specification.display_env,
            path=training_specification.path,
            custom_name=training_specification.custom_heuristic_name,
            max_n_jobs=self.env_specification.max_n_jobs,
            max_n_machines=self.env_specification.max_n_machines,
            max_time_ortools=training_specification.max_time_ortools,
            scaling_constant_ortools=training_specification.scaling_constant_ortools,
            ortools_strategy=training_specification.ortools_strategy,
            validate_on_total_data=training_specification.validate_on_total_data,
        )
        event_callback = EveryNTimesteps(n_steps=training_specification.validation_freq, callback=validation_callback)

        # Creating the vectorized environments
        classVecEnv = SubprocVecEnv
        if training_specification.vecenv_type == "dummy":
            classVecEnv = DummyVecEnv
        vec_env = classVecEnv([make_proc_env(problem_description, self.env_specification) for _ in range(self.n_workers)])

        # Finally, we can build our PPO
        if self.model is None:
            env_specification = self.env_specification
            agent_specification = self.agent_specification
            if agent_specification.fe_type == "dgl":
                fe_type = FeaturesExtractorDGL
            elif agent_specification.fe_type == "tokengt":
                fe_type = FeaturesExtractorTokenGT
            else:
                print("unknown fe_type: ", agent_specification.fe_type)

            if agent_specification.fe_type == "dgl":
                fe_kwargs = {
                    "input_dim_features_extractor": env_specification.n_features,
                    "gconv_type": agent_specification.gconv_type,
                    "graph_pooling": agent_specification.graph_pooling,
                    "freeze_graph": agent_specification.freeze_graph,
                    "graph_has_relu": agent_specification.graph_has_relu,
                    "device": agent_specification.device,
                    "max_n_nodes": env_specification.max_n_nodes,
                    "max_n_machines": env_specification.max_n_machines,
                    "n_mlp_layers_features_extractor": agent_specification.n_mlp_layers_features_extractor,
                    "activation_features_extractor": agent_specification.activation_fn_graph,
                    "n_layers_features_extractor": agent_specification.n_layers_features_extractor,
                    "hidden_dim_features_extractor": agent_specification.hidden_dim_features_extractor,
                    "n_attention_heads": agent_specification.n_attention_heads,
                    "reverse_adj": agent_specification.reverse_adj,
                    "residual": agent_specification.residual_gnn,
                    "normalize": agent_specification.normalize_gnn,
                    "conflicts": agent_specification.conflicts,
                }
            elif agent_specification.fe_type == "tokengt":
                fe_kwargs = {
                    "input_dim_features_extractor": env_specification.n_features,
                    "device": agent_specification.device,
                    "max_n_nodes": env_specification.max_n_nodes,
                    "max_n_machines": env_specification.max_n_machines,
                    "conflicts": agent_specification.conflicts,
                    "encoder_layers": agent_specification.n_layers_features_extractor,
                    "encoder_embed_dim": agent_specification.hidden_dim_features_extractor,
                    "encoder_ffn_embed_dim": agent_specification.hidden_dim_features_extractor,
                    "encoder_attention_heads": agent_specification.n_attention_heads,
                    "activation_fn": agent_specification.activation_fn_graph,
                    "lap_node_id": True,
                    "lap_node_id_k": agent_specification.lap_node_id_k,
                    "lap_node_id_sign_flip": True,
                    "type_id": True,
                    "transformer_flavor": agent_specification.transformer_flavor,
                    "layer_pooling": agent_specification.layer_pooling,
                    "dropout": agent_specification.dropout,
                    "attention_dropout": agent_specification.dropout,
                    "act_dropout": agent_specification.dropout,
                    "cache_lap_node_id": agent_specification.cache_lap_node_id,
                }
            if agent_specification.rpo:
                policy = RPOPolicy
            else:
                policy = Policy
            self.model = MaskablePPOCustom(
                policy,
                vec_env,
                learning_rate=agent_specification.lr,
                # learning_rate=partial(lr_schedule_linear, agent_specification.lr, 1e-9, 0.1),
                n_steps=agent_specification.n_steps_episode,
                batch_size=agent_specification.batch_size,
                n_epochs=agent_specification.n_epochs,
                gamma=agent_specification.gamma,
                gae_lambda=1,  # To use same vanilla advantage function
                clip_range=agent_specification.clip_range,
                ent_coef=agent_specification.ent_coef,
                vf_coef=agent_specification.vf_coef,
                normalize_advantage=agent_specification.normalize_advantage,
                policy_kwargs={
                    "optimizer_kwargs": {
                        "fe_lr": agent_specification.fe_lr,
                        "lr": agent_specification.lr,
                    },
                    "features_extractor_class": fe_type,
                    "features_extractor_kwargs": fe_kwargs,
                    "optimizer_class": agent_specification.optimizer_class,
                    "activation_fn": agent_specification.activation_fn,
                    "net_arch": agent_specification.net_arch,
                },
                verbose=2,
                device=agent_specification.device,
            )
            if agent_specification.rpo:
                self.model.set_rpo_smoothing_param(agent_specification.rpo_smoothing_param)

        # Load the vectorized environments in the existing model
        else:
            self.model.set_env(vec_env)

        # Launching training
        self.model.learn(training_specification.total_timesteps, callback=event_callback)

    def predict(self, problem_description):
        # Creating an environment on which we will run the inference
        env = Env(problem_description, self.env_specification)

        # Running the inference loop
        observation = env.reset()
        done = False
        while not done:
            action_masks = get_action_masks(env)
            action, _ = self.model.predict(observation, deterministic=True, action_masks=action_masks)
            observation, reward, done, info = env.step(action)

        return env.get_solution()
