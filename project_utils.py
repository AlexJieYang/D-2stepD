"""Input configuration and descriptive statistics for the notebooks."""
from pathlib import Path
import json
import os
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_FILES = {'aps_citations': 'aps-dataset-citations-2010.zip', 'aps_nodes': 'nodepro2010.zip', 'blogs_edges': 'blogs_edges.txt', 'email_edges': 'email_edges.txt', 'wiki_edges': 'wiki_edges.txt', 'blogs_metrics': 'blogs_metrics.csv', 'email_metrics': 'email_metrics.csv', 'wiki_metrics': 'wiki_metrics.csv', 'aps_overlap': 'aps_overlap.csv', 'blogs_overlap': 'blogs_overlap.csv', 'email_overlap': 'email_overlap.csv', 'wiki_overlap': 'wiki_overlap.csv'}

def settings():
    path = Path(os.environ.get("RESEARCH_CONFIG", ROOT / "config.json")).expanduser()
    config = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    return path.resolve().parent, config

def configured_directory(key, default, environment):
    base, config = settings()
    directory = Path(os.environ.get(environment, config.get(key, default))).expanduser()
    return directory if directory.is_absolute() else base / directory

SEED = int(os.environ.get("RESEARCH_SEED", settings()[1].get("seed", 2026)))

def input_path(key):
    directory = configured_directory("data_dir", "data", "RESEARCH_DATA_DIR")
    path = directory / DATA_FILES[key]
    if not path.is_file():
        raise FileNotFoundError(f"Input {key}: {path}")
    return path

def load_table(key):
    path = input_path(key)
    frame = pd.read_excel(path) if path.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(path)
    schema = json.loads((ROOT / "input_schema.json").read_text(encoding="utf-8"))
    required = schema[key].get("required_columns", [])
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Input {key} is missing columns: {missing}")
    return frame

def output_path(name):
    directory = configured_directory("output_dir", "outputs", "RESEARCH_OUTPUT_DIR")
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name

def calculateCI(data, method="mean", n=1000, seed=SEED):
    """Percentile bootstrap interval using N draws from N finite observations."""
    values = np.asarray(data, dtype=float).ravel()
    values = values[np.isfinite(values)]
    if method not in {"mean", "median"}:
        raise ValueError("method must be mean or median")
    if n < 1:
        raise ValueError("n must be positive")
    if not len(values):
        return np.nan, np.nan
    statistic = np.mean if method == "mean" else np.median
    rng = np.random.default_rng(seed)
    statistics = [statistic(rng.choice(values, size=len(values), replace=True)) for _ in range(n)]
    return tuple(np.percentile(statistics, [2.5, 97.5]))

def mean_error(data, n=1000):
    """Lower and upper distances from the finite-sample mean to its 95% interval."""
    values = np.asarray(data, dtype=float).ravel()
    values = values[np.isfinite(values)]
    if not len(values):
        return np.array([np.nan, np.nan])
    low, high = calculateCI(values, "mean", n)
    center = values.mean()
    return np.maximum([center - low, high - center], 0)

def standard_error(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return np.std(values, ddof=1) / np.sqrt(len(values)) if len(values) > 1 else np.nan

def percentile_column(frame, column):
    values = frame[column]
    count = values.notna().sum()
    frame[column + "_percentile"] = ((values.rank() - 1) / (count - 1) * 100 if count > 1 else np.nan)

def positive_fraction(values):
    values = pd.Series(values).dropna()
    return values.ne(0).mean() if len(values) else np.nan
