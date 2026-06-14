from __future__ import annotations

import csv
import math
import os
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import Ridge


BASE_SEED = 229114322
QUICK_MODE = os.getenv("PAPER75_QUICK", "0") == "1"
SEED_COUNT = int(os.getenv("PAPER75_SEED_COUNT", "1" if QUICK_MODE else "7"))
SEEDS = list(range(SEED_COUNT))
TRAIN_SCENARIOS = int(os.getenv("PAPER75_TRAIN_SCENARIOS", "10" if QUICK_MODE else "38"))
EVAL_SCENARIOS = int(os.getenv("PAPER75_EVAL_SCENARIOS", "4" if QUICK_MODE else "12"))
ABLATION_SCENARIOS = int(os.getenv("PAPER75_ABLATION_SCENARIOS", "3" if QUICK_MODE else "8"))
STRESS_SCENARIOS = int(os.getenv("PAPER75_STRESS_SCENARIOS", "3" if QUICK_MODE else "8"))
STEPS = int(os.getenv("PAPER75_STEPS", "44" if QUICK_MODE else "58"))
DT = 0.035

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

METHODS = [
    "visible_state_mpc",
    "history_rnn_estimator",
    "particle_filter_memory",
    "graph_dynamics_baseline",
    "ensemble_uncertainty_planner",
    "action_conditioned_memory",
    "oracle_latent_state",
]

ABLATION_METHODS = [
    "action_conditioned_full",
    "action_conditioned_no_action_conditioning",
    "action_conditioned_no_branch_memory",
    "action_conditioned_no_diagnostic_probes",
    "action_conditioned_no_material_memory",
    "action_conditioned_no_contact_memory",
    "action_conditioned_no_uncertainty_term",
]

STRESS_METHODS = [
    "particle_filter_memory",
    "ensemble_uncertainty_planner",
    "action_conditioned_memory",
    "oracle_latent_state",
]

ACTIONS = [
    "pull_high",
    "pull_low",
    "center_pull",
    "gentle_relax_pull",
    "fixture_avoid_pull",
    "two_end_stretch",
    "diagnostic_branch_pull",
]

FAILURES = [
    "excessive_stretch",
    "fixture_snag",
    "force_limit",
    "energy_overshoot",
    "wrong_memory_branch",
    "occlusion_miss",
    "shape_failure",
    "unstable_fold",
]

OBJECTS = ["rope", "cloth_strip", "elastic_band", "deformable_sheet"]


@dataclass(frozen=True)
class SplitSpec:
    name: str
    task_id: int
    hidden_scale: float
    occlusion: float
    material_shift: float
    fixture_strength: float
    force_limit: float
    noise: float


@dataclass(frozen=True)
class DeformableConfig:
    seed: int
    scenario: int
    split: SplitSpec
    object_type: str
    positions: np.ndarray
    velocities: np.ndarray
    base_positions: np.ndarray
    target_positions: np.ndarray
    memory_shape: np.ndarray
    edges: np.ndarray
    rest_lengths: np.ndarray
    observed_mask: np.ndarray
    history_signal: np.ndarray
    true_memory: float
    hidden_contact: float
    stiffness: float
    damping: float
    friction: float
    mass: float
    force_limit: float
    fixture: Tuple[float, float, float]
    noise: float
    success_threshold: float


@dataclass
class RolloutOutcome:
    success: int
    shape_error: float
    memory_error: float
    damage: float
    max_stretch: float
    contact_rate: float
    force_clip_rate: float
    strain_energy: float
    final_progress: float
    diagnostic_count: int
    failures: np.ndarray
    trajectory: str


@dataclass
class PlannerModels:
    history_model: Ridge
    graph_model: Ridge
    action_model: Ridge
    ensemble_models: List[Ridge]
    history_mean: np.ndarray
    history_std: np.ndarray
    graph_mean: np.ndarray
    graph_std: np.ndarray
    action_mean: np.ndarray
    action_std: np.ndarray


SPLITS = [
    SplitSpec("nominal_visible_state", 0, 0.14, 0.04, 0.08, 0.10, 1.00, 0.003),
    SplitSpec("hidden_strain_memory", 1, 0.55, 0.09, 0.16, 0.18, 0.90, 0.006),
    SplitSpec("occluded_contact_memory", 2, 0.45, 0.38, 0.16, 0.34, 0.86, 0.009),
    SplitSpec("material_shift", 3, 0.34, 0.12, 0.55, 0.24, 0.74, 0.008),
    SplitSpec("combined_memory_stress", 4, 0.68, 0.42, 0.58, 0.50, 0.66, 0.012),
]
SPLIT_BY_NAME = {split.name: split for split in SPLITS}


def ci95(values: Sequence[float]) -> float:
    vals = np.array(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * np.std(vals, ddof=1) / math.sqrt(len(vals)))


def rng_for(seed: int, scenario: int, *parts: object) -> np.random.Generator:
    offset = 0
    for part in parts:
        for idx, char in enumerate(str(part)):
            offset += (idx + 17) * ord(char)
    return np.random.default_rng(BASE_SEED + 65537 * seed + 4099 * scenario + offset)


def object_graph(object_type: str) -> Tuple[np.ndarray, np.ndarray, float]:
    if object_type == "rope":
        xs = np.linspace(-0.34, 0.26, 10)
        positions = np.stack([xs, 0.025 * np.sin(np.linspace(0.0, math.pi, 10))], axis=1)
        edges = [(idx, idx + 1) for idx in range(9)]
        threshold = 0.150
    elif object_type == "cloth_strip":
        xs = np.linspace(-0.32, 0.24, 6)
        ys = np.array([-0.045, 0.045])
        positions = np.array([[x, y] for x in xs for y in ys], dtype=float)
        edges = []
        for ix in range(6):
            edges.append((2 * ix, 2 * ix + 1))
            if ix < 5:
                edges.extend([(2 * ix, 2 * (ix + 1)), (2 * ix + 1, 2 * (ix + 1) + 1)])
                edges.extend([(2 * ix, 2 * (ix + 1) + 1), (2 * ix + 1, 2 * (ix + 1))])
        threshold = 0.130
    elif object_type == "elastic_band":
        angles = np.linspace(0, 2 * math.pi, 12, endpoint=False)
        positions = np.stack([-0.05 + 0.24 * np.cos(angles), 0.08 * np.sin(angles)], axis=1)
        edges = [(idx, (idx + 1) % 12) for idx in range(12)]
        edges += [(idx, (idx + 2) % 12) for idx in range(12)]
        threshold = 0.120
    else:
        xs = np.linspace(-0.30, 0.24, 4)
        ys = np.linspace(-0.075, 0.075, 3)
        positions = np.array([[x, y] for x in xs for y in ys], dtype=float)
        edges = []
        for ix in range(4):
            for iy in range(3):
                idx = 3 * ix + iy
                if ix < 3:
                    edges.append((idx, 3 * (ix + 1) + iy))
                if iy < 2:
                    edges.append((idx, idx + 1))
                if ix < 3 and iy < 2:
                    edges.append((idx, 3 * (ix + 1) + iy + 1))
                if ix < 3 and iy > 0:
                    edges.append((idx, 3 * (ix + 1) + iy - 1))
        threshold = 0.135
    return positions.astype(float), np.array(edges, dtype=int), threshold


def memory_profile(base: np.ndarray, object_type: str, memory: float, contact: float) -> np.ndarray:
    xs = base[:, 0]
    xnorm = (xs - float(xs.min())) / max(1e-6, float(xs.max() - xs.min()))
    profile = np.sin(math.pi * xnorm)
    if object_type == "rope":
        y = 0.13 * memory * profile + 0.035 * contact * np.sin(2 * math.pi * xnorm)
        x = -0.025 * abs(memory) * profile
    elif object_type == "cloth_strip":
        row = np.sign(base[:, 1] + 1e-6)
        crease = np.exp(-((xnorm - 0.54) ** 2) / 0.035)
        y = 0.10 * memory * crease * row + 0.030 * contact * profile
        x = -0.018 * abs(memory) * crease
    elif object_type == "elastic_band":
        radial = np.stack([base[:, 0] + 0.05, base[:, 1]], axis=1)
        scale = np.linalg.norm(radial, axis=1, keepdims=True) + 1e-6
        direction = radial / scale
        return 0.055 * memory * direction + np.stack([0.018 * contact * profile, 0.030 * contact * np.cos(2 * math.pi * xnorm)], axis=1)
    else:
        row = np.sign(base[:, 1] + 1e-6)
        y = 0.085 * memory * profile * row + 0.040 * contact * np.sin(2 * math.pi * xnorm)
        x = -0.020 * abs(memory) * profile
    return np.stack([x, y], axis=1)


def rest_lengths_from_memory(base: np.ndarray, edges: np.ndarray, memory: float, rng: np.random.Generator) -> np.ndarray:
    rest = np.linalg.norm(base[edges[:, 1]] - base[edges[:, 0]], axis=1)
    centers = 0.5 * (base[edges[:, 0], 0] + base[edges[:, 1], 0])
    xnorm = (centers - float(base[:, 0].min())) / max(1e-6, float(base[:, 0].max() - base[:, 0].min()))
    bias = 1.0 + 0.085 * memory * np.sin(math.pi * xnorm) + rng.normal(0.0, 0.010, size=len(edges))
    return np.clip(rest * bias, rest * 0.78, rest * 1.28)


def build_config(split: SplitSpec, seed: int, scenario: int, purpose: str, stress_level: float | None = None) -> DeformableConfig:
    rng = rng_for(seed, scenario, split.name if stress_level is None else f"{split.name}_{stress_level}", purpose)
    object_type = OBJECTS[(scenario + seed) % len(OBJECTS)]
    base, edges, threshold = object_graph(object_type)
    if stress_level is None:
        hidden_scale = split.hidden_scale
        occlusion = split.occlusion
        material = split.material_shift
        fixture_strength = split.fixture_strength
        force_limit = split.force_limit
        noise = split.noise
    else:
        hidden_scale = 0.16 + 0.68 * stress_level
        occlusion = 0.04 + 0.48 * stress_level
        material = 0.08 + 0.62 * stress_level
        fixture_strength = 0.10 + 0.56 * stress_level
        force_limit = 1.0 - 0.39 * stress_level
        noise = 0.003 + 0.014 * stress_level
    sign = -1.0 if rng.random() < 0.5 else 1.0
    memory = float(sign * hidden_scale * rng.uniform(0.65, 1.08))
    contact = float((1.0 if rng.random() < 0.5 else -1.0) * fixture_strength * rng.uniform(0.55, 1.15))
    memory_delta = memory_profile(base, object_type, memory, contact)
    memory_shape = base + memory_delta
    visible_flatten = 0.20 if split.name != "nominal_visible_state" else 0.45
    initial = base + visible_flatten * memory_delta + rng.normal(0.0, 0.004 + noise, size=base.shape)
    target = base.copy()
    target[:, 0] += 0.25 if object_type != "elastic_band" else 0.16
    target[:, 1] *= 0.35
    target[:, 1] += 0.025 * np.sin(np.linspace(0.0, math.pi, len(target)))
    stiffness = float(58.0 * rng.normal(1.0 + 0.35 * material, 0.08 + 0.04 * material))
    damping = float(2.2 * rng.normal(1.0 + 0.20 * material, 0.06))
    friction = float(np.clip(0.82 + 0.40 * material + rng.normal(0.0, 0.05), 0.55, 1.55))
    mass = float(np.clip(1.0 + 0.28 * material + rng.normal(0.0, 0.06), 0.75, 1.75))
    fx = float(0.02 + rng.normal(0.0, 0.018))
    fy = float(0.11 * np.sign(contact + 1e-6) + rng.normal(0.0, 0.020))
    radius = float(0.040 + 0.045 * fixture_strength + rng.normal(0.0, 0.004))
    observed_mask = make_observed_mask(initial, occlusion, rng)
    history_signal = np.array(
        [
            0.66 * memory + rng.normal(0.0, 0.12 + 0.08 * hidden_scale),
            0.48 * contact + rng.normal(0.0, 0.10 + 0.07 * fixture_strength),
            hidden_scale + rng.normal(0.0, 0.06),
            material + rng.normal(0.0, 0.06),
            float(np.mean(observed_mask)),
        ],
        dtype=float,
    )
    return DeformableConfig(
        seed=seed,
        scenario=scenario,
        split=split,
        object_type=object_type,
        positions=initial.astype(float),
        velocities=np.zeros_like(initial, dtype=float),
        base_positions=base.astype(float),
        target_positions=target.astype(float),
        memory_shape=memory_shape.astype(float),
        edges=edges,
        rest_lengths=rest_lengths_from_memory(base, edges, memory, rng),
        observed_mask=observed_mask,
        history_signal=history_signal,
        true_memory=memory,
        hidden_contact=contact,
        stiffness=max(18.0, stiffness),
        damping=max(0.8, damping),
        friction=friction,
        mass=mass,
        force_limit=float(26.0 * force_limit),
        fixture=(fx, fy, radius),
        noise=noise,
        success_threshold=float(threshold * (1.0 + 0.22 * hidden_scale + 0.10 * occlusion)),
    )


def make_observed_mask(positions: np.ndarray, occlusion: float, rng: np.random.Generator) -> np.ndarray:
    mask = np.ones(len(positions), dtype=bool)
    if occlusion <= 0.06:
        return mask
    center_x = rng.uniform(float(np.percentile(positions[:, 0], 35)), float(np.percentile(positions[:, 0], 72)))
    radius = 0.035 + 0.16 * occlusion
    hidden = np.abs(positions[:, 0] - center_x) < radius
    dropout = rng.random(len(positions)) < max(0.0, occlusion - 0.28) * 0.25
    mask[hidden | dropout] = False
    if np.sum(mask) < max(3, len(mask) // 3):
        keep = np.argsort(np.abs(positions[:, 0] - center_x))[-max(3, len(mask) // 3) :]
        mask[keep] = True
    return mask


def observed_positions(cfg: DeformableConfig) -> np.ndarray:
    rng = rng_for(cfg.seed, cfg.scenario, cfg.split.name, cfg.object_type, "obs")
    obs = cfg.positions + rng.normal(0.0, cfg.noise, size=cfg.positions.shape)
    imputed = obs.copy()
    if np.any(~cfg.observed_mask):
        visible = cfg.observed_mask
        shift = np.mean(obs[visible] - cfg.base_positions[visible], axis=0)
        imputed[~visible] = cfg.base_positions[~visible] + shift
    return imputed


def feature_vector(cfg: DeformableConfig, mode: str) -> np.ndarray:
    obs = observed_positions(cfg)
    visible = cfg.observed_mask
    edge_lengths = np.linalg.norm(obs[cfg.edges[:, 1]] - obs[cfg.edges[:, 0]], axis=1)
    base_lengths = np.linalg.norm(cfg.base_positions[cfg.edges[:, 1]] - cfg.base_positions[cfg.edges[:, 0]], axis=1)
    stretch = edge_lengths / np.maximum(base_lengths, 1e-6)
    xs = obs[:, 0]
    ys = obs[:, 1]
    sorted_idx = np.argsort(xs)
    curvature = np.diff(ys[sorted_idx], n=2) if len(ys) >= 3 else np.array([0.0])
    type_onehot = np.zeros(len(OBJECTS), dtype=float)
    type_onehot[OBJECTS.index(cfg.object_type)] = 1.0
    task_onehot = np.zeros(len(SPLITS), dtype=float)
    task_onehot[cfg.split.task_id] = 1.0
    common = np.array(
        [
            float(np.mean(xs[visible])),
            float(np.mean(ys[visible])),
            float(np.std(xs[visible])),
            float(np.std(ys[visible])),
            float(np.max(xs[visible]) - np.min(xs[visible])),
            float(np.max(ys[visible]) - np.min(ys[visible])),
            float(np.mean(stretch)),
            float(np.std(stretch)),
            float(np.max(stretch)),
            float(np.mean(curvature)),
            float(np.std(curvature)),
            float(np.mean(visible)),
            cfg.fixture[0],
            cfg.fixture[1],
            cfg.fixture[2],
            cfg.force_limit / 26.0,
        ],
        dtype=float,
    )
    if mode == "graph":
        return np.concatenate([common, type_onehot, task_onehot])
    if mode == "history":
        return np.concatenate([common, cfg.history_signal[:3], type_onehot, task_onehot])
    return np.concatenate([common, cfg.history_signal, type_onehot, task_onehot])


def standardize_train(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    std[std < 1e-6] = 1.0
    return (x - mean) / std, mean, std


def standardize_apply(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (x - mean) / std


def train_models(seed: int) -> PlannerModels:
    configs: List[DeformableConfig] = []
    for split in SPLITS:
        for idx in range(TRAIN_SCENARIOS):
            configs.append(build_config(split, seed, 10_000 + 97 * split.task_id + idx, "train"))
    y = np.array([cfg.true_memory for cfg in configs], dtype=float)
    history_x = np.vstack([feature_vector(cfg, "history") for cfg in configs])
    graph_x = np.vstack([feature_vector(cfg, "graph") for cfg in configs])
    action_x = np.vstack([feature_vector(cfg, "action") for cfg in configs])
    history_xs, history_mean, history_std = standardize_train(history_x)
    graph_xs, graph_mean, graph_std = standardize_train(graph_x)
    action_xs, action_mean, action_std = standardize_train(action_x)
    history_model = Ridge(alpha=0.85).fit(history_xs, y)
    graph_model = Ridge(alpha=1.10).fit(graph_xs, y)
    action_model = Ridge(alpha=0.45).fit(action_xs, y)
    ensemble_models: List[Ridge] = []
    rng = rng_for(seed, 99_001, "ensemble_bootstrap")
    for member in range(5):
        idx = rng.choice(len(y), size=len(y), replace=True)
        ensemble_models.append(Ridge(alpha=0.55 + 0.15 * member).fit(action_xs[idx], y[idx]))
    return PlannerModels(
        history_model=history_model,
        graph_model=graph_model,
        action_model=action_model,
        ensemble_models=ensemble_models,
        history_mean=history_mean,
        history_std=history_std,
        graph_mean=graph_mean,
        graph_std=graph_std,
        action_mean=action_mean,
        action_std=action_std,
    )


def predict_memory(cfg: DeformableConfig, models: PlannerModels, method: str, ablation: str | None = None) -> Tuple[List[float], float]:
    if method == "oracle_latent_state":
        return [cfg.true_memory], 0.0
    history = float(models.history_model.predict(standardize_apply(feature_vector(cfg, "history")[None, :], models.history_mean, models.history_std))[0])
    graph = float(models.graph_model.predict(standardize_apply(feature_vector(cfg, "graph")[None, :], models.graph_mean, models.graph_std))[0])
    action = float(models.action_model.predict(standardize_apply(feature_vector(cfg, "action")[None, :], models.action_mean, models.action_std))[0])
    ens = [
        float(model.predict(standardize_apply(feature_vector(cfg, "action")[None, :], models.action_mean, models.action_std))[0])
        for model in models.ensemble_models
    ]
    uncertainty = float(np.std(ens))
    if method == "visible_state_mpc":
        return [0.0], 0.34 + abs(graph) * 0.15
    if method == "history_rnn_estimator":
        return [history], 0.20 + abs(history - graph) * 0.25
    if method == "graph_dynamics_baseline":
        return [graph], 0.22 + abs(history - graph) * 0.20
    if method == "particle_filter_memory":
        spread = max(0.18, 0.65 * abs(history - graph) + 0.12)
        return [history - spread, history, history + spread], spread
    if method == "ensemble_uncertainty_planner":
        return ens, max(uncertainty, 0.08)
    # Proposed and ablations.
    center = 0.62 * action + 0.24 * history + 0.14 * graph
    spread = max(0.08, uncertainty + 0.06)
    if ablation == "action_conditioned_no_action_conditioning":
        center = graph
        spread += 0.12
    elif ablation == "action_conditioned_no_branch_memory":
        return [center], spread + 0.10
    elif ablation == "action_conditioned_no_material_memory":
        center = 0.50 * action + 0.50 * history
        spread += 0.08
    elif ablation == "action_conditioned_no_contact_memory":
        center = 0.70 * action
        spread += 0.08
    if ablation == "action_conditioned_no_uncertainty_term":
        return [center], 0.0
    return [center - spread, center, center + spread], spread


def estimated_config(cfg: DeformableConfig, memory_est: float) -> DeformableConfig:
    obs = observed_positions(cfg)
    base = cfg.base_positions.copy()
    contact_est = float(np.clip(cfg.history_signal[1], -0.9, 0.9))
    mem_shape = base + memory_profile(base, cfg.object_type, memory_est, contact_est)
    rng = rng_for(cfg.seed, cfg.scenario, cfg.split.name, cfg.object_type, "estimate", f"{memory_est:.3f}")
    rest = rest_lengths_from_memory(base, cfg.edges, memory_est, rng)
    stiff_scale = 1.0 + 0.10 * np.tanh(cfg.history_signal[3] if len(cfg.history_signal) > 3 else 0.0)
    return replace(
        cfg,
        positions=obs,
        velocities=np.zeros_like(obs),
        memory_shape=mem_shape,
        rest_lengths=rest,
        true_memory=memory_est,
        hidden_contact=contact_est,
        stiffness=max(18.0, cfg.stiffness * stiff_scale),
        damping=cfg.damping,
        friction=cfg.friction,
    )


def control_indices(pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs = pos[:, 0]
    left = np.where(xs <= np.percentile(xs, 18))[0]
    right = np.where(xs >= np.percentile(xs, 82))[0]
    center = np.where(np.abs(xs - np.median(xs)) <= max(0.02, np.std(xs) * 0.35))[0]
    if len(center) == 0:
        center = np.array([int(np.argmin(np.abs(xs - np.median(xs))))])
    return left, right, center


def action_targets(
    action: str,
    step: int,
    pos: np.ndarray,
    cfg: DeformableConfig,
    probe_signal: float,
    left: np.ndarray,
    right: np.ndarray,
    center: np.ndarray,
) -> List[Tuple[np.ndarray, np.ndarray, float]]:
    targets: List[Tuple[np.ndarray, np.ndarray, float]] = []
    goal_x = float(np.max(cfg.target_positions[:, 0]))
    fixture_y = cfg.fixture[1]
    if action == "pull_high":
        route_y, gain = 0.17, 1.0
    elif action == "pull_low":
        route_y, gain = -0.17, 1.0
    elif action == "center_pull":
        route_y, gain = 0.0, 0.92
    elif action == "gentle_relax_pull":
        route_y, gain = 0.02 * np.sign(-cfg.true_memory), 0.62
    elif action == "fixture_avoid_pull":
        route_y, gain = -0.19 * np.sign(fixture_y + 1e-6), 0.88
    elif action == "two_end_stretch":
        route_y, gain = 0.0, 0.72
        targets.append((left, np.array([float(np.min(cfg.base_positions[:, 0])) - 0.10, -0.02]), gain))
    else:
        if step < max(8, STEPS // 4):
            targets.append((center, np.array([float(np.mean(pos[center, 0])), 0.12]), 0.55))
            return targets
        route_y = -0.18 if probe_signal > 0.0 else 0.18
        gain = 0.86
    targets.append((right, np.array([goal_x, route_y]), gain))
    return targets


def simulate(cfg: DeformableConfig, action: str, memory_estimate: float) -> RolloutOutcome:
    pos = cfg.positions.copy()
    vel = cfg.velocities.copy()
    left, right, center = control_indices(pos)
    edge_i = cfg.edges[:, 0]
    edge_j = cfg.edges[:, 1]
    probe_signal = 0.0
    max_stretch = 1.0
    max_energy = 0.0
    contact_steps = 0
    clipped_steps = 0
    max_abs_y = float(np.max(np.abs(pos[:, 1])))
    samples: List[str] = []
    route_sign = 0.0
    for step in range(STEPS):
        forces = -cfg.damping * vel
        delta = pos[edge_j] - pos[edge_i]
        length = np.sqrt(np.sum(delta * delta, axis=1)) + 1e-8
        unit = delta / length[:, None]
        stretch = length / np.maximum(1e-6, cfg.rest_lengths)
        max_stretch = max(max_stretch, float(np.max(stretch)))
        spring = cfg.stiffness * (length - cfg.rest_lengths)
        rel_vel = np.sum((vel[edge_j] - vel[edge_i]) * unit, axis=1)
        damp = 0.45 * cfg.damping * rel_vel
        edge_force = (spring + damp)[:, None] * unit
        np.add.at(forces, edge_i, edge_force)
        np.add.at(forces, edge_j, -edge_force)
        strain_energy = float(np.sum(0.5 * cfg.stiffness * (length - cfg.rest_lengths) ** 2))
        forces += 6.5 * (cfg.memory_shape - pos)
        forces += -0.30 * cfg.friction * vel
        fixture = np.array(cfg.fixture[:2], dtype=float)
        radius = cfg.fixture[2]
        d = pos - fixture
        dist = np.linalg.norm(d, axis=1) + 1e-8
        inside = dist < radius
        if np.any(inside):
            contact_steps += 1
            normal = d[inside] / dist[inside, None]
            depth = radius - dist[inside]
            forces[inside] += normal * (105.0 * depth[:, None])
            vel[inside] *= 0.88
        if action == "diagnostic_branch_pull" and step == max(8, STEPS // 4):
            probe_signal = float(np.mean(pos[center, 1] - cfg.positions[center, 1]) + 0.45 * cfg.true_memory)
        targets = action_targets(action, step, pos, cfg, probe_signal, left, right, center)
        for idx, target, gain in targets:
            err = target[None, :] - pos[idx]
            ctrl = gain * (78.0 * err - 4.2 * vel[idx])
            norm = np.linalg.norm(ctrl, axis=1)
            over = norm > cfg.force_limit
            if np.any(over):
                clipped_steps += 1
                ctrl[over] *= (cfg.force_limit / (norm[over, None] + 1e-8))
            forces[idx] += ctrl
            if len(idx) > 0:
                route_sign = float(np.sign(target[1]))
        accel = forces / cfg.mass
        vel += DT * accel
        vel *= 0.985
        pos += DT * vel
        pos[:, 0] = np.clip(pos[:, 0], -0.55, 0.62)
        pos[:, 1] = np.clip(pos[:, 1], -0.36, 0.36)
        max_abs_y = max(max_abs_y, float(np.max(np.abs(pos[:, 1]))))
        max_energy = max(max_energy, float(strain_energy))
        if step % max(1, STEPS // 5) == 0 or step == STEPS - 1:
            err = float(np.mean(np.linalg.norm(pos - cfg.target_positions, axis=1)))
            samples.append(f"{step}:err={err:.3f}:stretch={max_stretch:.2f}:contact={int(np.any(inside))}")
    shape_error = float(np.mean(np.linalg.norm(pos - cfg.target_positions, axis=1)))
    target_span = max(1e-6, float(np.max(cfg.target_positions[:, 0]) - np.min(cfg.base_positions[:, 0])))
    final_progress = float(np.clip((np.mean(pos[:, 0]) - np.mean(cfg.base_positions[:, 0])) / target_span, 0.0, 1.4))
    contact_rate = contact_steps / STEPS
    clip_rate = clipped_steps / STEPS
    diagnostic_count = int(action == "diagnostic_branch_pull")
    wrong_branch = bool(route_sign != 0.0 and np.sign(route_sign) == np.sign(cfg.true_memory) and shape_error > cfg.success_threshold)
    excessive_stretch = max_stretch > 3.25
    fixture_snag = contact_rate > 0.46
    force_limit = clip_rate > 0.28
    energy_overshoot = max_energy > 8.5 + 7.0 * cfg.split.material_shift
    occlusion_miss = float(np.mean(cfg.observed_mask)) < 0.70 and shape_error > cfg.success_threshold * 0.92
    shape_failure = shape_error > cfg.success_threshold
    unstable_fold = max_abs_y > 0.31
    damage = float(excessive_stretch or fixture_snag or energy_overshoot or unstable_fold)
    success = int((not shape_failure) and damage == 0.0 and final_progress > 0.12 and not force_limit)
    failures = np.array(
        [
            excessive_stretch,
            fixture_snag,
            force_limit,
            energy_overshoot,
            wrong_branch,
            occlusion_miss,
            shape_failure,
            unstable_fold,
        ],
        dtype=int,
    )
    if success == 0 and not failures.any():
        failures[FAILURES.index("shape_failure")] = 1
    return RolloutOutcome(
        success=success,
        shape_error=shape_error,
        memory_error=abs(memory_estimate - cfg.true_memory),
        damage=damage,
        max_stretch=float(max_stretch),
        contact_rate=float(contact_rate),
        force_clip_rate=float(clip_rate),
        strain_energy=float(max_energy),
        final_progress=final_progress,
        diagnostic_count=diagnostic_count,
        failures=failures,
        trajectory=";".join(samples),
    )


def score_outcome(outcome: RolloutOutcome, uncertainty: float, allow_probe: bool) -> float:
    probe_penalty = 0.020 * outcome.diagnostic_count if allow_probe else 0.055 * outcome.diagnostic_count
    return (
        1.15 * outcome.success
        - 1.40 * outcome.shape_error
        - 0.42 * outcome.damage
        - 0.18 * outcome.force_clip_rate
        - 0.11 * uncertainty
        - probe_penalty
    )


def route_for_action(action: str, cfg: DeformableConfig, memory_estimate: float) -> float:
    if action == "pull_high":
        return 1.0
    if action == "pull_low":
        return -1.0
    if action == "fixture_avoid_pull":
        return float(-np.sign(cfg.fixture[1] + 1e-6))
    if action == "diagnostic_branch_pull":
        return float(-np.sign(memory_estimate + 1e-6))
    return 0.0


def surrogate_predict(cfg: DeformableConfig, action: str, memory_estimate: float, uncertainty: float) -> RolloutOutcome:
    visible_fraction = float(np.mean(cfg.observed_mask))
    route = route_for_action(action, cfg, memory_estimate)
    difficulty = (
        0.050
        + 0.055 * abs(memory_estimate)
        + 0.045 * (1.0 - visible_fraction)
        + 0.030 * cfg.split.material_shift
        + 0.025 * cfg.split.fixture_strength
    )
    wrong_branch = bool(route != 0.0 and np.sign(route) == np.sign(memory_estimate) and abs(memory_estimate) > 0.18)
    route_bonus = 0.030 if route != 0.0 and not wrong_branch else -0.020
    if action == "diagnostic_branch_pull":
        route_bonus += max(0.0, 0.060 - 0.035 * uncertainty)
    if action == "gentle_relax_pull":
        route_bonus += 0.015 - 0.025 * abs(memory_estimate)
    if action == "two_end_stretch":
        route_bonus += 0.020 if cfg.object_type == "elastic_band" else -0.035
    fixture_penalty = 0.045 if route != 0.0 and np.sign(route) == np.sign(cfg.fixture[1]) else 0.005
    force_penalty = 0.050 if cfg.force_limit < 18.0 and action in {"pull_high", "pull_low", "two_end_stretch"} else 0.0
    shape_error = float(max(0.025, difficulty + fixture_penalty + force_penalty - route_bonus))
    contact_rate = float(max(0.0, fixture_penalty * 2.2 + 0.10 * cfg.split.fixture_strength))
    clip_rate = float(max(0.0, force_penalty * 3.0 + 0.08 * (1.0 - cfg.force_limit / 26.0)))
    damage = float(contact_rate > 0.18 or clip_rate > 0.26 or shape_error > cfg.success_threshold * 1.25)
    success = int(shape_error < cfg.success_threshold and damage == 0.0)
    failures = np.array(
        [
            action == "two_end_stretch" and cfg.object_type != "elastic_band",
            contact_rate > 0.18,
            clip_rate > 0.26,
            shape_error > cfg.success_threshold * 1.35,
            wrong_branch,
            visible_fraction < 0.70 and shape_error > cfg.success_threshold * 0.95,
            success == 0,
            False,
        ],
        dtype=int,
    )
    return RolloutOutcome(
        success=success,
        shape_error=shape_error,
        memory_error=abs(memory_estimate - cfg.true_memory),
        damage=damage,
        max_stretch=1.0 + 0.40 * float(failures[0]),
        contact_rate=contact_rate,
        force_clip_rate=clip_rate,
        strain_energy=4.0 * shape_error,
        final_progress=0.65 if success else 0.35,
        diagnostic_count=int(action == "diagnostic_branch_pull"),
        failures=failures,
        trajectory="surrogate",
    )


def choose_action(method: str, cfg: DeformableConfig, models: PlannerModels, ablation: str | None = None) -> Tuple[str, float, float, np.ndarray]:
    memories, uncertainty = predict_memory(cfg, models, method, ablation)
    if method == "oracle_latent_state":
        best_action = ACTIONS[0]
        best_score = -1e9
        best_failures = np.zeros(len(FAILURES), dtype=int)
        for action in ACTIONS:
            outcome = simulate(cfg, action, cfg.true_memory)
            score = score_outcome(outcome, 0.0, allow_probe=True)
            if score > best_score:
                best_score = score
                best_action = action
                best_failures = outcome.failures
        return best_action, cfg.true_memory, 0.0, best_failures
    if ablation == "action_conditioned_no_diagnostic_probes":
        action_space = [a for a in ACTIONS if a != "diagnostic_branch_pull"]
    elif method in {"visible_state_mpc", "graph_dynamics_baseline"}:
        action_space = [a for a in ACTIONS if a != "diagnostic_branch_pull"]
    else:
        action_space = ACTIONS
    allow_probe = method == "action_conditioned_memory" or (ablation is not None and ablation != "action_conditioned_no_diagnostic_probes")
    best_action = action_space[0]
    best_score = -1e9
    best_pred: RolloutOutcome | None = None
    for action in action_space:
        pred_scores: List[float] = []
        pred_outcomes: List[RolloutOutcome] = []
        for memory in memories:
            est = estimated_config(cfg, memory)
            pred = surrogate_predict(est, action, memory, uncertainty)
            pred_outcomes.append(pred)
            pred_scores.append(score_outcome(pred, uncertainty, allow_probe))
        score = float(np.mean(pred_scores))
        if method in {"ensemble_uncertainty_planner", "particle_filter_memory"} or ablation != "action_conditioned_no_uncertainty_term":
            score -= 0.18 * float(np.std(pred_scores))
        if score > best_score:
            best_score = score
            best_action = action
            best_pred = pred_outcomes[int(np.argmax(pred_scores))]
    assert best_pred is not None
    memory_est = float(np.mean(memories))
    return best_action, memory_est, uncertainty, best_pred.failures


def evaluate_method(method: str, cfg: DeformableConfig, models: PlannerModels, ablation: str | None = None) -> Dict[str, str]:
    action, memory_est, uncertainty, pred_failures = choose_action(method, cfg, models, ablation)
    actual = simulate(cfg, action, memory_est)
    method_name = ablation or method
    return {
        "seed": str(cfg.seed),
        "scenario": str(cfg.scenario),
        "scenario_id": f"{cfg.split.name}_{cfg.seed}_{cfg.scenario}_{cfg.object_type}",
        "split": cfg.split.name,
        "object_type": cfg.object_type,
        "method": method_name,
        "chosen_action": action,
        "true_memory": f"{cfg.true_memory:.5f}",
        "estimated_memory": f"{memory_est:.5f}",
        "uncertainty": f"{uncertainty:.5f}",
        "visible_fraction": f"{float(np.mean(cfg.observed_mask)):.5f}",
        "success": str(actual.success),
        "shape_error": f"{actual.shape_error:.5f}",
        "memory_error": f"{actual.memory_error:.5f}",
        "damage": f"{actual.damage:.5f}",
        "max_stretch": f"{actual.max_stretch:.5f}",
        "contact_rate": f"{actual.contact_rate:.5f}",
        "force_clip_rate": f"{actual.force_clip_rate:.5f}",
        "strain_energy": f"{actual.strain_energy:.5f}",
        "final_progress": f"{actual.final_progress:.5f}",
        "diagnostic_count": str(actual.diagnostic_count),
        "actual_failures": ";".join(name for name, active in zip(FAILURES, actual.failures) if active),
        "predicted_failures": ";".join(name for name, active in zip(FAILURES, pred_failures) if active),
        "actual_failure_bits": "".join(str(int(x)) for x in actual.failures),
        "predicted_failure_bits": "".join(str(int(x)) for x in pred_failures),
        "trajectory": actual.trajectory,
    }


def mechanism_macro_f1(rows: Sequence[Dict[str, str]]) -> float:
    if not rows:
        return 0.0
    pred = np.array([[int(ch) for ch in row["predicted_failure_bits"]] for row in rows], dtype=int)
    true = np.array([[int(ch) for ch in row["actual_failure_bits"]] for row in rows], dtype=int)
    f1s: List[float] = []
    for idx in range(true.shape[1]):
        tp = float(np.sum((pred[:, idx] == 1) & (true[:, idx] == 1)))
        fp = float(np.sum((pred[:, idx] == 1) & (true[:, idx] == 0)))
        fn = float(np.sum((pred[:, idx] == 0) & (true[:, idx] == 1)))
        if tp == 0.0 and fp == 0.0 and fn == 0.0:
            f1s.append(1.0)
        elif tp == 0.0:
            f1s.append(0.0)
        else:
            precision = tp / max(1e-9, tp + fp)
            recall = tp / max(1e-9, tp + fn)
            f1s.append(2.0 * precision * recall / max(1e-9, precision + recall))
    return float(np.mean(f1s))


def build_seed_metrics(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault((row["method"], row["split"], row["seed"]), []).append(row)
    metrics: List[Dict[str, str]] = []
    for (method, split, seed), group in sorted(grouped.items()):
        vals = lambda key: [float(row[key]) for row in group]
        metrics.append(
            {
                "method": method,
                "split": split,
                "seed": seed,
                "episodes": str(len(group)),
                "success": f"{float(np.mean(vals('success'))):.5f}",
                "shape_error": f"{float(np.mean(vals('shape_error'))):.5f}",
                "memory_error": f"{float(np.mean(vals('memory_error'))):.5f}",
                "mechanism_macro_f1": f"{mechanism_macro_f1(group):.5f}",
                "tail_risk": f"{1.0 - float(np.mean(vals('success'))):.5f}",
                "damage_rate": f"{float(np.mean(vals('damage'))):.5f}",
                "force_clip_rate": f"{float(np.mean(vals('force_clip_rate'))):.5f}",
                "diagnostic_rate": f"{float(np.mean(vals('diagnostic_count'))):.5f}",
            }
        )
    return metrics


def build_summary(seed_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    for row in seed_rows:
        grouped.setdefault((row["method"], row["split"]), []).append(row)
    summary: List[Dict[str, str]] = []
    metrics = [
        "success",
        "shape_error",
        "memory_error",
        "mechanism_macro_f1",
        "tail_risk",
        "damage_rate",
        "force_clip_rate",
        "diagnostic_rate",
    ]
    for (method, split), group in sorted(grouped.items()):
        item = {"method": method, "split": split, "seeds": str(len(group))}
        for metric in metrics:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        summary.append(item)
    return summary


def build_pairwise(seed_rows: Sequence[Dict[str, str]], reference: str = "action_conditioned_memory") -> List[Dict[str, str]]:
    by_key = {(row["method"], row["split"], row["seed"]): row for row in seed_rows}
    methods = sorted({row["method"] for row in seed_rows})
    splits = sorted({row["split"] for row in seed_rows})
    seeds = sorted({row["seed"] for row in seed_rows})
    out: List[Dict[str, str]] = []
    for split in splits:
        for method in methods:
            if method == reference:
                continue
            success_diffs: List[float] = []
            memory_diffs: List[float] = []
            f1_diffs: List[float] = []
            damage_reductions: List[float] = []
            for seed in seeds:
                ref = by_key.get((reference, split, seed))
                other = by_key.get((method, split, seed))
                if ref is None or other is None:
                    continue
                success_diffs.append(float(ref["success"]) - float(other["success"]))
                memory_diffs.append(float(other["memory_error"]) - float(ref["memory_error"]))
                f1_diffs.append(float(ref["mechanism_macro_f1"]) - float(other["mechanism_macro_f1"]))
                damage_reductions.append(float(other["damage_rate"]) - float(ref["damage_rate"]))
            if success_diffs:
                out.append(
                    {
                        "split": split,
                        "reference": reference,
                        "comparison": method,
                        "paired_success_diff": f"{float(np.mean(success_diffs)):.5f}",
                        "ci95_success_diff": f"{ci95(success_diffs):.5f}",
                        "paired_memory_error_reduction": f"{float(np.mean(memory_diffs)):.5f}",
                        "paired_mechanism_f1_diff": f"{float(np.mean(f1_diffs)):.5f}",
                        "paired_damage_reduction": f"{float(np.mean(damage_reductions)):.5f}",
                        "reference_better_seeds": str(sum(1 for diff in success_diffs if diff > 0.0)),
                        "seeds": str(len(success_diffs)),
                    }
                )
    return out


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_bar(summary: Sequence[Dict[str, str]], split: str, metric: str, path: Path, title: str) -> None:
    rows = [row for row in summary if row["split"] == split]
    rows = sorted(rows, key=lambda row: float(row[f"mean_{metric}"]), reverse=metric == "success")
    labels = [row["method"].replace("_", "\n") for row in rows]
    means = [float(row[f"mean_{metric}"]) for row in rows]
    cis = [float(row[f"ci95_{metric}"]) for row in rows]
    plt.figure(figsize=(10, 4.6))
    plt.bar(range(len(rows)), means, yerr=cis, color="#486b73", edgecolor="#1d2d31", capsize=3)
    plt.xticks(range(len(rows)), labels, fontsize=7)
    plt.ylabel(metric.replace("_", " "))
    plt.title(title)
    plt.ylim(0, 1.05 if metric in {"success", "mechanism_macro_f1"} else None)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_stress(stress_summary: Sequence[Dict[str, str]], path: Path) -> None:
    plt.figure(figsize=(7.8, 4.8))
    for method in sorted({row["method"] for row in stress_summary}):
        rows = sorted([row for row in stress_summary if row["method"] == method], key=lambda row: float(row["stress_level"]))
        xs = [float(row["stress_level"]) for row in rows]
        ys = [float(row["mean_success"]) for row in rows]
        es = [float(row["ci95_success"]) for row in rows]
        plt.errorbar(xs, ys, yerr=es, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("combined memory stress level")
    plt.ylabel("closed-loop success")
    plt.title("Paper 75 deformable-memory stress sweep")
    plt.ylim(-0.02, 1.02)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def decide(summary: Sequence[Dict[str, str]], pairwise: Sequence[Dict[str, str]]) -> Tuple[str, str]:
    combined = [row for row in summary if row["split"] == "combined_memory_stress"]
    proposed = [row for row in combined if row["method"] == "action_conditioned_memory"][0]
    non_oracle = [row for row in combined if row["method"] not in {"action_conditioned_memory", "oracle_latent_state"}]
    best = max(non_oracle, key=lambda row: float(row["mean_success"]))
    pair = [row for row in pairwise if row["split"] == "combined_memory_stress" and row["comparison"] == best["method"]][0]
    prop_success = float(proposed["mean_success"])
    best_success = float(best["mean_success"])
    paired = float(pair["paired_success_diff"])
    paired_ci = float(pair["ci95_success_diff"])
    memory_reduction = float(pair["paired_memory_error_reduction"])
    f1_diff = float(pair["paired_mechanism_f1_diff"])
    damage_reduction = float(pair["paired_damage_reduction"])
    if (
        prop_success - best_success >= 0.045
        and paired - paired_ci > 0.0
        and memory_reduction >= -0.005
        and f1_diff >= -0.015
        and damage_reduction >= -0.020
    ):
        return (
            "STRONG_REVISE",
            f"action_conditioned_memory clears strongest non-oracle baseline {best['method']} on combined_memory_stress by "
            f"{prop_success - best_success:.3f} success with paired diff {paired:.3f}+/-{paired_ci:.3f}, "
            "but lacks real robot and external deformable-manipulation benchmark validation.",
        )
    return (
        "KILL_ARCHIVE",
        f"action_conditioned_memory does not clear strongest non-oracle baseline {best['method']} decisively on combined_memory_stress "
        f"(proposed={prop_success:.3f}, best_baseline={best_success:.3f}, paired diff={paired:.3f}+/-{paired_ci:.3f}, "
        f"memory_reduction={memory_reduction:.3f}, mechanism_f1_diff={f1_diff:.3f}, damage_reduction={damage_reduction:.3f}).",
    )


def negative_cases(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    selected = [
        row
        for row in rows
        if row["split"] == "combined_memory_stress" and row["method"] == "action_conditioned_memory" and row["success"] == "0"
    ]
    out: List[Dict[str, str]] = []
    for row in selected[:12]:
        out.append(
            {
                "seed": row["seed"],
                "scenario_id": row["scenario_id"],
                "object_type": row["object_type"],
                "chosen_action": row["chosen_action"],
                "actual_failures": row["actual_failures"],
                "shape_error": row["shape_error"],
                "memory_error": row["memory_error"],
                "lesson": "action-conditioned memory estimated a branch but the selected action still failed deformable contact dynamics",
            }
        )
    return out or [
        {
            "seed": "",
            "scenario_id": "",
            "object_type": "",
            "chosen_action": "",
            "actual_failures": "",
            "shape_error": "",
            "memory_error": "",
            "lesson": "no negative cases found",
        }
    ]


def group_rows(rows: Sequence[Dict[str, str]], keys: Sequence[str]) -> Dict[Tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    return grouped


def main() -> None:
    start = time.time()
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    models_by_seed = {seed: train_models(seed) for seed in SEEDS}
    rollout_rows: List[Dict[str, str]] = []
    training_rows: List[Dict[str, str]] = []
    for seed in SEEDS:
        training_rows.append(
            {
                "seed": str(seed),
                "train_scenarios_per_split": str(TRAIN_SCENARIOS),
                "train_rows": str(TRAIN_SCENARIOS * len(SPLITS)),
                "quick_mode": str(QUICK_MODE),
            }
        )
        for split in SPLITS:
            for local_idx in range(EVAL_SCENARIOS):
                cfg = build_config(split, seed, 1000 * split.task_id + local_idx, "eval")
                for method in METHODS:
                    rollout_rows.append(evaluate_method(method, cfg, models_by_seed[seed]))
    seed_rows = build_seed_metrics(rollout_rows)
    summary = build_summary(seed_rows)
    pairwise = build_pairwise(seed_rows)

    ablation_rows_raw: List[Dict[str, str]] = []
    combined = SPLIT_BY_NAME["combined_memory_stress"]
    for seed in SEEDS:
        for local_idx in range(ABLATION_SCENARIOS):
            cfg = build_config(combined, seed, 7000 + local_idx, "ablation")
            for ablation in ABLATION_METHODS:
                ablation_rows_raw.append(evaluate_method("action_conditioned_memory", cfg, models_by_seed[seed], ablation=ablation))
    ablation_seed = build_seed_metrics(ablation_rows_raw)
    ablation_summary = build_summary(ablation_seed)

    stress_raw: List[Dict[str, str]] = []
    for level in ([0.0, 1.0] if QUICK_MODE else np.linspace(0.0, 1.0, 6)):
        for seed in SEEDS:
            for local_idx in range(STRESS_SCENARIOS):
                cfg = build_config(combined, seed, 9000 + int(100 * level) + local_idx, "stress", stress_level=float(level))
                for method in STRESS_METHODS:
                    row = evaluate_method(method, cfg, models_by_seed[seed])
                    row["stress_level"] = f"{float(level):.2f}"
                    stress_raw.append(row)
    stress_seed = build_seed_metrics(stress_raw)
    stress_summary: List[Dict[str, str]] = []
    for (method, stress_level), group in sorted(group_rows(stress_raw, ["method", "stress_level"]).items()):
        seed_group = build_seed_metrics(group)
        item = {"method": method, "stress_level": stress_level, "seeds": str(len({row["seed"] for row in group}))}
        for metric in ["success", "shape_error", "memory_error", "mechanism_macro_f1", "tail_risk", "damage_rate"]:
            vals = [float(row[metric]) for row in seed_group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        stress_summary.append(item)

    write_csv(RESULTS / "rollouts.csv", rollout_rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", summary)
    write_csv(RESULTS / "pairwise_stats.csv", pairwise)
    write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows_raw)
    write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)
    write_csv(RESULTS / "stress_sweep_raw.csv", stress_raw)
    write_csv(RESULTS / "stress_sweep.csv", stress_summary)
    write_csv(FIGURES / "stress_curve_data.csv", stress_summary)
    write_csv(RESULTS / "negative_cases.csv", negative_cases(rollout_rows))
    write_csv(
        RESULTS / "training_summary.csv",
        [
            {
                "quick_mode": str(QUICK_MODE),
                "seeds": ";".join(str(seed) for seed in SEEDS),
                "seed_count": str(len(SEEDS)),
                "train_scenarios_per_split": str(TRAIN_SCENARIOS),
                "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                "ablation_scenarios": str(ABLATION_SCENARIOS),
                "stress_scenarios": str(STRESS_SCENARIOS),
                "splits": str(len(SPLITS)),
                "methods": str(len(METHODS)),
                "ablation_methods": str(len(ABLATION_METHODS)),
                "actions": str(len(ACTIONS)),
                "sim_steps": str(STEPS),
                "dt": f"{DT:.5f}",
            }
        ],
    )

    plot_bar(summary, "combined_memory_stress", "success", FIGURES / "deformable_memory_final_success.png", "Paper 75 combined-memory closed-loop success")
    plot_bar(summary, "combined_memory_stress", "memory_error", FIGURES / "deformable_memory_error.png", "Paper 75 hidden-memory estimation error")
    plot_bar(ablation_summary, "combined_memory_stress", "success", FIGURES / "deformable_memory_ablation_success.png", "Paper 75 action-conditioned memory ablations")
    plot_stress(stress_summary, FIGURES / "deformable_memory_stress_sweep.png")

    decision, reason = decide(summary, pairwise)
    elapsed = time.time() - start
    combined_rows = [row for row in summary if row["split"] == "combined_memory_stress"]
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 75 deformable_memory_under_action real deformable-physics rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Rollout rows: {len(rollout_rows)}\n")
        f.write(f"Seed metric rows: {len(seed_rows)}\n")
        f.write(f"Ablation rows: {len(ablation_rows_raw)}\n")
        f.write(f"Stress rows: {len(stress_raw)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write(f"Training scenarios per split: {TRAIN_SCENARIOS}\n")
        f.write(f"Evaluation scenarios per split: {EVAL_SCENARIOS}\n")
        f.write(f"Runtime seconds: {elapsed:.2f}\n\n")
        f.write("Combined-memory-stress summary:\n")
        for row in sorted(combined_rows, key=lambda item: -float(item["mean_success"])):
            f.write(
                f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                f"shape_error={row['mean_shape_error']} memory_error={row['mean_memory_error']} "
                f"mechanism_f1={row['mean_mechanism_macro_f1']} damage={row['mean_damage_rate']}\n"
            )
    print(f"wrote Paper 75 deformable-memory evidence to {RESULTS}")
    print(f"terminal recommendation: {decision}")
    print(reason)


if __name__ == "__main__":
    main()
