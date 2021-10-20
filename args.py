import argparse

parser = argparse.ArgumentParser(
    description="Arguments for the main experiment, using PPO to solve a Job Shop Scheduling Problem"
)

# General problem arguments
parser.add_argument("--n_j", type=int, default=5, help="Number of jobs")
parser.add_argument("--n_m", type=int, default=5, help="Number of machines")
parser.add_argument("--transition_model_config", type=str, default="L2D", help="Which transition model to use")
parser.add_argument(
    "--reward_model_config", type=str, default="L2D", help="Which reward model to use, from L2D, Sparse, Tassel"
)
parser.add_argument("--seed", type=int, default=42, help="Random seed")
parser.add_argument("--path", type=str, default="saved_networks/default_net", help="Path to saved network")
parser.add_argument("--fixed_benchmark", default=False, action="store_true", help="Test model on fixed or random benchmark")
parser.add_argument(
    "--add_force_insert_boolean",
    default=False,
    action="store_true",
    help="Add a bool in action space for forced insertion use",
)
parser.add_argument(
    "--full_force_insert",
    default=False,
    action="store_true",
    help="Action are forced to be inserted",
)
parser.add_argument("--slot_locking", default=False, action="store_true", help="Add a bool in act. space for slot locking")
parser.add_argument(
    "--features",
    type=str,
    nargs="+",
    default=[
        "duration",
        "total_job_time",
        "total_machine_time",
        "job_completion_percentage",
        "machine_completion_percentage",
        "mopnr",
        "mwkr",
    ],
    help="The features we want to have as input of features_extractor",
)

# Agent arguments
parser.add_argument(
    "--gconv_type", type=str, default="gatv2", help="Graph convolutional neural network type: gin for GIN, gatv2 for GATV2"
)
parser.add_argument("--graph_pooling", type=str, default="max", help="which pooling to use (avg or max)")
parser.add_argument("--mlp_act", type=str, default="tanh", help="agent mlp extractor activation type, relu or tanh")
parser.add_argument(
    "--graph_has_relu", action="store_true", help="whether graph feature extractor has activations between layers"
)

# Training arguments
parser.add_argument("--total_timesteps", type=int, default=int(1e4), help="Number of training env timesteps")
parser.add_argument("--n_epochs", type=int, default=1, help="Number of epochs for updating the PPO parameters")
parser.add_argument("--n_steps_episode", type=int, default=1024, help="Number of steps per episode.")
parser.add_argument("--batch_size", type=int, default=128, help="Batch size during training of PPO")
parser.add_argument("--gamma", type=float, default=1, help="Discount factor")
parser.add_argument("--clip_range", type=float, default=0.2, help="Clipping parameter")
parser.add_argument("--target_kl", type=float, default=0.2, help="Limit the KL divergence between updates")
parser.add_argument("--ent_coef", type=float, default=0.005, help="Entropy coefficient")
parser.add_argument("--vf_coef", type=float, default=0.5, help="Value function coefficient")
parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
parser.add_argument("--optimizer", type=str, default="adam", help="Which optimizer to use")

parser.add_argument("--n_test_env", type=int, default=20, help="Number of testing environments during traing")
parser.add_argument("--eval_freq", type=int, default=1000, help="Number of steps between each evaluation during training")

parser.add_argument(
    "--dont_normalize_input", default=False, action="store_true", help="Default is dividing input by constant"
)
parser.add_argument("--fixed_problem", default=False, action="store_true", help="Fix affectations and durations for train")

parser.add_argument("--n_workers", type=int, default=1, help="Number of CPU cores for simulating environment")
parser.add_argument("--multiprocessing", default=False, action="store_true", help="Wether to use multiprocessing or not")
parser.add_argument("--cpu", default=False, action="store_true", help="Wether to use CPU or not")

parser.add_argument(
    "--retrain",
    default=False,
    action="store_true",
    help="If true, the script checks for already existing model and use it as a basis for training",
)

parser.add_argument("--freeze_graph", default=False, action="store_true", help="Freezes graph during training")

parser.add_argument("--custom_heuristic_name", default="None", help="Which custom heuristic to run")

# Testing arguments
parser.add_argument("--n_test_problems", type=int, default=100, help="Number of problems for testing")

# Other
parser.add_argument("--exp_name_appendix", type=str, help="Appendix for the name of the experience")
parser.add_argument("--stable_baselines3_localisation", type=str, help="If using custom SB3, specify here the path")

# Parsing
args, _ = parser.parse_known_args()

if hasattr(args, "n_j") and hasattr(args, "n_m"):
    exp_name = f"{args.n_j}j{args.n_m}m_{args.seed}seed_{args.transition_model_config}_{args.reward_model_config}_{args.gconv_type}_{args.graph_pooling}"

    if args.fixed_benchmark:
        exp_name += "_FB"
    if args.dont_normalize_input:
        exp_name += "_DNI"
    if args.fixed_problem:
        exp_name += "_FP"
    if args.freeze_graph:
        exp_name += "_FG"
    if args.add_force_insert_boolean:
        exp_name += "_FI"
    if args.slot_locking:
        exp_name += "_SL"
    if args.exp_name_appendix is not None:
        exp_name += "_" + args.exp_name_appendix

else:
    exp_name = ""

# Modify path if there is a custom SB3 library path specified
if hasattr(args, "stable_baselines3_localisation") and args.stable_baselines3_localisation is not None:
    import sys

    sys.path.insert(0, args.stable_baselines3_localisation + "/stable-baselines3/")
    sys.path.insert(0, args.stable_baselines3_localisation + "stable-baselines3/")
    sys.path.insert(0, args.stable_baselines3_localisation)
    import stable_baselines3

    print(f"Stable Baselines 3 imported from : {stable_baselines3.__file__}")

# checking incompatibility
if args.add_force_insert_boolean and args.slot_locking:
    raise Exception("You can't use force insert boolean and slot locking in the same script")
if args.full_force_insert and args.add_force_insert_boolean:
    raise Exception("You can't use force insert boolean and full force insert in the same script")
if args.full_force_insert and args.slot_locking:
    raise Exception("You can't use full force insert and slot locking in the same script")

args.input_list = args.features
