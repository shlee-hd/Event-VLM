#!/usr/bin/env python3
"""
Auto-tuning script for Event-VLM using Optuna.
Optimizes hyperparameters for maximum AUC with efficiency constraints.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import optuna
from optuna.trial import Trial
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner
from omegaconf import OmegaConf

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, EventVLMConfig
from experiments.evaluate import evaluate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventVLMObjective:
    """
    Optuna objective for Event-VLM hyperparameter optimization.
    
    Optimizes for weighted combination of AUC and FPS.
    """
    
    def __init__(
        self,
        base_config: EventVLMConfig,
        search_space: Dict[str, Dict],
        objectives: list = ["auc", "fps"],
        objective_weights: list = [1.0, 0.5],
        quick_eval: bool = True
    ):
        self.base_config = base_config
        self.search_space = search_space
        self.objectives = objectives
        self.objective_weights = objective_weights
        self.quick_eval = quick_eval
        
        # Track best results
        self.best_score = float("-inf")
        self.best_config = None
        self.trial_history = []
    
    def __call__(self, trial: Trial) -> float:
        """
        Objective function for Optuna.
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Combined objective score
        """
        # Sample hyperparameters
        config = self._sample_config(trial)
        
        # Run evaluation
        try:
            metrics = evaluate(
                config=config,
                output_dir=None,
                quick=self.quick_eval,
                max_videos=50 if self.quick_eval else None
            )
        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {e}")
            return float("-inf")
        
        # Compute combined objective
        score = 0.0
        for obj, weight in zip(self.objectives, self.objective_weights):
            if obj in metrics:
                score += weight * metrics[obj]
        
        # Track history
        trial_result = {
            "trial": trial.number,
            "params": trial.params,
            "metrics": metrics,
            "score": score
        }
        self.trial_history.append(trial_result)
        
        # Update best
        if score > self.best_score:
            self.best_score = score
            self.best_config = config
            logger.info(f"New best score: {score:.4f}")
        
        return score
    
    def _sample_config(self, trial: Trial) -> EventVLMConfig:
        """Sample configuration from search space."""
        # Deep copy base config
        config = OmegaConf.structured(self.base_config)
        config = OmegaConf.to_object(config)
        
        # Sample detector hyperparameters
        if "lambda_crit" in self.search_space:
            sp = self.search_space["lambda_crit"]
            config.detector.risk_weights.critical = trial.suggest_float(
                "lambda_crit", sp["low"], sp["high"]
            )
        
        if "lambda_high" in self.search_space:
            sp = self.search_space["lambda_high"]
            config.detector.risk_weights.high = trial.suggest_float(
                "lambda_high", sp["low"], sp["high"]
            )
        
        if "conf_threshold" in self.search_space:
            sp = self.search_space["conf_threshold"]
            config.detector.conf_threshold = trial.suggest_float(
                "conf_threshold", sp["low"], sp["high"]
            )
        
        # Sample pruning hyperparameters
        if "alpha_base" in self.search_space:
            sp = self.search_space["alpha_base"]
            config.pruning.alpha_base = trial.suggest_float(
                "alpha_base", sp["low"], sp["high"]
            )
        
        if "beta" in self.search_space:
            sp = self.search_space["beta"]
            config.pruning.beta = trial.suggest_float(
                "beta", sp["low"], sp["high"]
            )
        
        if "min_tokens" in self.search_space:
            sp = self.search_space["min_tokens"]
            config.pruning.min_tokens = trial.suggest_int(
                "min_tokens", sp["low"], sp["high"]
            )
        
        # Categorical parameters
        if "detector_model" in self.search_space:
            choices = self.search_space["detector_model"]["choices"]
            config.detector.model = trial.suggest_categorical(
                "detector_model", choices
            )
        
        return config


def run_optimization(
    config_path: str,
    n_trials: int = 100,
    study_name: str = "event_vlm_tuning",
    storage: Optional[str] = None,
    output_dir: str = "outputs/tuning",
    quick: bool = True
) -> Dict[str, Any]:
    """
    Run hyperparameter optimization.
    
    Args:
        config_path: Path to base config
        n_trials: Number of trials
        study_name: Optuna study name
        storage: SQLite storage path
        output_dir: Output directory
        quick: Use quick evaluation
        
    Returns:
        Best parameters and results
    """
    # Load base config
    config = load_config(config_path)
    
    # Get search space from config
    search_space = config.auto_tune.search_space
    objectives = config.auto_tune.objectives
    objective_weights = config.auto_tune.objective_weights
    
    logger.info(f"Starting optimization with {n_trials} trials")
    logger.info(f"Search space: {list(search_space.keys())}")
    logger.info(f"Objectives: {objectives} (weights: {objective_weights})")
    
    # Create objective
    objective = EventVLMObjective(
        base_config=config,
        search_space=search_space,
        objectives=objectives,
        objective_weights=objective_weights,
        quick_eval=quick
    )
    
    # Create or load study
    if storage:
        storage = f"sqlite:///{storage}"
    
    study = optuna.create_study(
        study_name=study_name,
        storage=storage,
        sampler=TPESampler(seed=config.seed),
        pruner=MedianPruner(),
        direction="maximize",
        load_if_exists=True
    )
    
    # Run optimization
    study.optimize(
        objective,
        n_trials=n_trials,
        show_progress_bar=True,
        catch=(Exception,)
    )
    
    # Get best results
    best_trial = study.best_trial
    best_params = best_trial.params
    best_value = best_trial.value
    
    logger.info("=" * 50)
    logger.info("Optimization Complete")
    logger.info("=" * 50)
    logger.info(f"Best trial: {best_trial.number}")
    logger.info(f"Best score: {best_value:.4f}")
    logger.info(f"Best parameters:")
    for key, value in best_params.items():
        logger.info(f"  {key}: {value}")
    
    # Save results
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save best config
    if objective.best_config:
        best_config_path = output_dir / f"best_config_{timestamp}.yaml"
        OmegaConf.save(OmegaConf.structured(objective.best_config), best_config_path)
        logger.info(f"Best config saved to {best_config_path}")
    
    # Save trial history
    history_path = output_dir / f"trial_history_{timestamp}.json"
    with open(history_path, "w") as f:
        json.dump(objective.trial_history, f, indent=2, default=str)
    
    # Save study statistics
    stats = {
        "study_name": study_name,
        "n_trials": len(study.trials),
        "best_trial": best_trial.number,
        "best_value": best_value,
        "best_params": best_params,
        "datetime": timestamp
    }
    
    stats_path = output_dir / f"study_stats_{timestamp}.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    return {
        "best_params": best_params,
        "best_value": best_value,
        "study": study,
        "history": objective.trial_history
    }


def visualize_study(study: optuna.Study, output_dir: str):
    """Generate visualization plots for the study."""
    try:
        from optuna.visualization import (
            plot_optimization_history,
            plot_param_importances,
            plot_parallel_coordinate,
            plot_contour
        )
        import plotly
        
        output_dir = Path(output_dir)
        
        # Optimization history
        fig = plot_optimization_history(study)
        fig.write_html(output_dir / "optimization_history.html")
        
        # Parameter importances
        fig = plot_param_importances(study)
        fig.write_html(output_dir / "param_importances.html")
        
        # Parallel coordinate
        fig = plot_parallel_coordinate(study)
        fig.write_html(output_dir / "parallel_coordinate.html")
        
        logger.info(f"Visualizations saved to {output_dir}")
        
    except ImportError:
        logger.warning("Plotly not installed. Skipping visualizations.")


def main():
    parser = argparse.ArgumentParser(description="Auto-tune Event-VLM")
    parser.add_argument(
        "--config",
        type=str,
        default="experiments/configs/base.yaml",
        help="Base config file"
    )
    parser.add_argument(
        "--n-trials",
        type=int,
        default=100,
        help="Number of optimization trials"
    )
    parser.add_argument(
        "--study-name",
        type=str,
        default="event_vlm_tuning",
        help="Optuna study name"
    )
    parser.add_argument(
        "--storage",
        type=str,
        default=None,
        help="SQLite database path for study persistence"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/tuning",
        help="Output directory"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use quick evaluation (fewer samples per trial)"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization plots"
    )
    
    args = parser.parse_args()
    
    # Run optimization
    results = run_optimization(
        config_path=args.config,
        n_trials=args.n_trials,
        study_name=args.study_name,
        storage=args.storage,
        output_dir=args.output_dir,
        quick=args.quick
    )
    
    # Generate visualizations
    if args.visualize and results.get("study"):
        visualize_study(results["study"], args.output_dir)
    
    print(f"\nOptimization complete!")
    print(f"Best score: {results['best_value']:.4f}")
    print(f"Best params: {results['best_params']}")


if __name__ == "__main__":
    main()
