"""
Evaluation metrics for Event-VLM.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve


class AUCMeter:
    """Meter for computing Area Under ROC Curve."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.predictions = []
        self.targets = []
    
    def update(self, preds: np.ndarray, targets: np.ndarray):
        """Update with batch of predictions and targets."""
        self.predictions.extend(preds.flatten().tolist())
        self.targets.extend(targets.flatten().tolist())
    
    def compute(self) -> Dict[str, float]:
        """Compute AUC and AP metrics."""
        if not self.predictions:
            return {"auc": 0.0, "ap": 0.0}
        
        preds = np.array(self.predictions)
        targets = np.array(self.targets)
        
        # Handle edge cases
        if len(np.unique(targets)) < 2:
            return {"auc": 0.0, "ap": 0.0}
        
        auc = roc_auc_score(targets, preds)
        ap = average_precision_score(targets, preds)
        
        return {"auc": auc, "ap": ap}


class CaptionMetrics:
    """
    Metrics for caption evaluation.
    Computes BLEU, METEOR, ROUGE-L, CIDEr scores.
    """
    
    def __init__(self):
        self.hypotheses = []
        self.references = []
        self._scorers = None
    
    def _init_scorers(self):
        """Initialize scorers lazily."""
        if self._scorers is not None:
            return
        
        try:
            from pycocoevalcap.bleu.bleu import Bleu
            from pycocoevalcap.meteor.meteor import Meteor
            from pycocoevalcap.rouge.rouge import Rouge
            from pycocoevalcap.cider.cider import Cider
            
            self._scorers = [
                (Bleu(4), ["BLEU-1", "BLEU-2", "BLEU-3", "BLEU-4"]),
                (Meteor(), "METEOR"),
                (Rouge(), "ROUGE-L"),
                (Cider(), "CIDEr"),
            ]
        except ImportError:
            print("pycocoevalcap not installed. Using simple metrics.")
            self._scorers = []
    
    def reset(self):
        self.hypotheses = []
        self.references = []
    
    def update(self, hypothesis: str, reference: str):
        """Update with a single hypothesis-reference pair."""
        self.hypotheses.append(hypothesis)
        self.references.append(reference)
    
    def update_batch(self, hypotheses: List[str], references: List[str]):
        """Update with batch of pairs."""
        self.hypotheses.extend(hypotheses)
        self.references.extend(references)
    
    def compute(self) -> Dict[str, float]:
        """Compute all caption metrics."""
        self._init_scorers()
        
        if not self.hypotheses:
            return {}
        
        # Format for pycocoevalcap
        gts = {i: [ref] for i, ref in enumerate(self.references)}
        res = {i: [hyp] for i, hyp in enumerate(self.hypotheses)}
        
        metrics = {}
        
        for scorer, name in self._scorers:
            try:
                score, _ = scorer.compute_score(gts, res)
                if isinstance(name, list):
                    for i, n in enumerate(name):
                        metrics[n] = score[i]
                else:
                    metrics[name] = score
            except Exception as e:
                print(f"Error computing {name}: {e}")
        
        return metrics
    
    @staticmethod
    def simple_bleu(hypothesis: str, reference: str, n: int = 4) -> float:
        """Simple BLEU score without external dependencies."""
        from collections import Counter
        
        hyp_tokens = hypothesis.lower().split()
        ref_tokens = reference.lower().split()
        
        if not hyp_tokens or not ref_tokens:
            return 0.0
        
        scores = []
        for i in range(1, n + 1):
            hyp_ngrams = Counter(
                tuple(hyp_tokens[j:j+i]) for j in range(len(hyp_tokens) - i + 1)
            )
            ref_ngrams = Counter(
                tuple(ref_tokens[j:j+i]) for j in range(len(ref_tokens) - i + 1)
            )
            
            overlap = sum((hyp_ngrams & ref_ngrams).values())
            total = sum(hyp_ngrams.values())
            
            scores.append(overlap / max(total, 1))
        
        # Geometric mean
        from math import exp, log
        if min(scores) > 0:
            return exp(sum(log(s) for s in scores) / len(scores))
        return 0.0


class TriggerReliabilityMeter:
    """Meter for measuring trigger (gating) reliability."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.true_positives = 0
        self.false_negatives = 0
        self.false_positives = 0
        self.true_negatives = 0
    
    def update(self, triggered: bool, has_hazard: bool):
        """Update with single sample."""
        if triggered and has_hazard:
            self.true_positives += 1
        elif not triggered and has_hazard:
            self.false_negatives += 1
        elif triggered and not has_hazard:
            self.false_positives += 1
        else:
            self.true_negatives += 1
    
    def compute(self) -> Dict[str, float]:
        """Compute recall and precision metrics."""
        tp = self.true_positives
        fn = self.false_negatives
        fp = self.false_positives
        tn = self.true_negatives
        
        recall = tp / max(tp + fn, 1)
        precision = tp / max(tp + fp, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-8)
        
        # For gating, high recall is critical
        return {
            "recall@trigger": recall,
            "precision@trigger": precision,
            "f1@trigger": f1,
            "miss_rate": fn / max(tp + fn, 1)
        }


def compute_metrics(
    predictions: List[Dict],
    ground_truth: List[Dict],
    include_caption: bool = True
) -> Dict[str, float]:
    """
    Compute all evaluation metrics.
    
    Args:
        predictions: List of prediction dicts
        ground_truth: List of ground truth dicts
        include_caption: Whether to include caption metrics
        
    Returns:
        Dict of metric name to value
    """
    auc_meter = AUCMeter()
    trigger_meter = TriggerReliabilityMeter()
    caption_metrics = CaptionMetrics() if include_caption else None
    
    for pred, gt in zip(predictions, ground_truth):
        # Detection/Classification metrics
        if "score" in pred and "label" in gt:
            auc_meter.update(
                np.array([pred["score"]]),
                np.array([gt["label"]])
            )
        
        # Trigger reliability
        if "triggered" in pred and "has_hazard" in gt:
            trigger_meter.update(pred["triggered"], gt["has_hazard"])
        
        # Caption metrics
        if caption_metrics and "caption" in pred and "caption" in gt:
            caption_metrics.update(pred["caption"], gt["caption"])
    
    # Aggregate
    metrics = {}
    metrics.update(auc_meter.compute())
    metrics.update(trigger_meter.compute())
    
    if caption_metrics:
        metrics.update(caption_metrics.compute())
    
    return metrics


def compute_efficiency_metrics(
    total_frames: int,
    processed_frames: int,
    event_frames: int,
    tokens_used: List[int],
    tokens_total: int,
    processing_time: float
) -> Dict[str, float]:
    """
    Compute efficiency metrics.
    
    Returns:
        Dict with FPS, token reduction, etc.
    """
    fps = processed_frames / max(processing_time, 1e-6)
    
    # Token reduction
    avg_tokens = np.mean(tokens_used) if tokens_used else tokens_total
    token_reduction = 1.0 - (avg_tokens / tokens_total)
    
    # FLOPs reduction (proportional to token reduction squared for attention)
    flops_reduction = 1.0 - ((avg_tokens / tokens_total) ** 2)
    
    # Event ratio (frames that triggered VLM)
    event_ratio = event_frames / max(processed_frames, 1)
    
    # Effective speedup (combining temporal and spatial efficiency)
    baseline_fps = fps / max(1.0 - event_ratio, 0.1)  # Estimate baseline
    speedup = fps / max(baseline_fps * event_ratio, 1e-6)
    
    return {
        "fps": fps,
        "token_reduction": token_reduction,
        "flops_reduction": flops_reduction,
        "event_ratio": event_ratio,
        "speedup": min(speedup, 20.0)  # Cap at 20x
    }
