"""Main application entry point."""
import argparse
import logging
import os
import sys

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import load_config, set_config
from src.utils.helpers import setup_logging
from src.jobs.mt_inversion_job import MTInversionJob

try:
    import MAGNETOTELLURIC_INVERSION_1D_GENETIC_ALGORITM.src.jobs.param_input as param_input
except ImportError:
    param_input = None

# Registry of available job processors
JOB_REGISTRY = {
    "MT_INVERSION_1D_GA": MTInversionJob,
}


def main():
    """Main application function."""
    params = param_input.get_param_input() if param_input and hasattr(param_input, "get_param_input") else {}

    parser = argparse.ArgumentParser(
        description="Pemodelan 1D Data Magnetotellurik Menggunakan Algoritma Genetika."
    )
    parser.add_argument(
        "--job-code",
        default="MT_INVERSION_1D_GA",
        help="Job code to execute (default: MT_INVERSION_1D_GA).",
    )
    parser.add_argument(
        "--source",
        choices=["postgre", "txt"],
        default=None,
        help="Observation data source: 'postgre' (PostgreSQL dad_dev.frequensi) or 'txt' (local file).",
    )
    parser.add_argument(
        "--data-path",
        default=None,
        help="Path to MT observation data file if using source=txt (default: data/data.txt).",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=None,
        help="Maximum GA iterations / generations (e.g. 100).",
    )
    parser.add_argument(
        "--population",
        type=int,
        default=None,
        help="Number of individuals in population (e.g. 50).",
    )
    parser.add_argument(
        "--layers",
        type=int,
        default=None,
        help="Number of earth layers (e.g. 7).",
    )
    parser.add_argument(
        "--crossover-rate",
        type=float,
        default=None,
        help="Crossover probability rate (e.g. 0.8).",
    )
    parser.add_argument(
        "--mutation-rate",
        type=float,
        default=None,
        help="Mutation probability rate (e.g. 0.3).",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable interactive GUI plot windows (useful for headless / background execution).",
    )
    args = parser.parse_args()

    logging.getLogger().handlers.clear()
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config = load_config(script_dir)
    set_config(config)
    setup_logging(config, script_dir)
    logger = logging.getLogger("mt_inversion")

    # Merge param_input values into config
    for k, v in params.items():
        if k not in config:
            config[k] = v

    # Apply CLI overrides
    if args.source:
        config["DATA_SOURCE"] = args.source
    if args.data_path:
        config["DATA_TXT_PATH"] = args.data_path
    if args.max_iter is not None:
        config["MAX_ITER"] = args.max_iter
    if args.population is not None:
        config["N_POPULASI"] = args.population
    if args.layers is not None:
        config["N_LAPIS"] = args.layers
    if args.crossover_rate is not None:
        config["CROSSOVER_RATE"] = args.crossover_rate
    if args.mutation_rate is not None:
        config["MUTATION_RATE"] = args.mutation_rate
    if args.no_plot:
        config["SHOW_PLOT"] = False

    # Route to the correct job class
    job_cls = JOB_REGISTRY.get(args.job_code)
    if not job_cls:
        raise ValueError(
            f"Unknown job code '{args.job_code}'. "
            f"Available: {', '.join(sorted(JOB_REGISTRY.keys()))}"
        )

    with job_cls(args.job_code, config, logger) as processor:
        processor.process()


if __name__ == "__main__":
    main()
