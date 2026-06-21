from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"


METHOD_ALIASES = {
    "visible_state_mpc": "visible-MPC",
    "damage_aware_visible_mpc": "damage-visible",
    "history_rnn_estimator": "history",
    "particle_filter_memory": "particle",
    "safety_constrained_particle_filter": "safe-particle",
    "graph_dynamics_baseline": "graph",
    "ensemble_uncertainty_planner": "ensemble",
    "robust_cem_surrogate": "robust-CEM",
    "action_conditioned_memory": "ACM-v4",
    "action_conditioned_memory_v5": "ACM-v5",
    "oracle_latent_state": "oracle",
    "action_conditioned_v5_full": "full-v5",
    "action_conditioned_v5_no_action_conditioning": "no-action",
    "action_conditioned_v5_no_branch_memory": "no-branch",
    "action_conditioned_v5_no_safety_gate": "no-safety",
    "action_conditioned_v5_no_diagnostic_gate": "no-diag-gate",
    "action_conditioned_v5_no_damage_penalty": "no-damage",
    "action_conditioned_v5_no_material_memory": "no-material",
    "action_conditioned_v5_no_uncertainty_term": "no-uncertainty",
}

SPLIT_ALIASES = {
    "nominal_visible_state": "nominal",
    "hidden_strain_memory": "hidden-strain",
    "occluded_contact_memory": "occluded-contact",
    "material_shift": "material-shift",
    "combined_memory_stress": "combined",
    "hard_regime": "hard-regime",
}


def read_csv(name: str) -> List[Dict[str, str]]:
    path = RESULTS / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def method_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(METHOD_ALIASES.get(name, name)) + "}"


def split_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(SPLIT_ALIASES.get(name, name)) + "}"


def f(value: str | float, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return tex_escape(value)


def pm(row: Dict[str, str], mean_key: str, ci_key: str, digits: int = 3) -> str:
    return f"${f(row[mean_key], digits)} \\pm {f(row[ci_key], digits)}$"


def summary_fields() -> Dict[str, str]:
    text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    fields = {"summary_text": text}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    return fields


def group_rows(rows: Iterable[Dict[str, str]], fields: Sequence[str]) -> Dict[tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row.get(field, "") for field in fields), []).append(row)
    return grouped


def figure(path: str, caption: str, width: str = "0.92") -> str:
    if not (FIGURES / path).exists():
        return ""
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width={width}\linewidth]{{../figures/{path}}}",
            r"\caption{" + caption + r"}",
            r"\end{figure}",
        ]
    )


def chunked_table(
    caption: str,
    label: str,
    headers: Sequence[str],
    align: str,
    rows: Sequence[Sequence[str]],
    chunk_size: int = 28,
    size: str = r"\scriptsize",
) -> str:
    if not rows:
        return ""
    out: List[str] = [size, r"\setlength{\tabcolsep}{2pt}"]
    for chunk_idx in range(0, len(rows), chunk_size):
        chunk = rows[chunk_idx : chunk_idx + chunk_size]
        out.append(r"\begin{center}")
        if chunk_idx == 0:
            out.append(r"\refstepcounter{table}\label{" + label + r"}\textbf{Table \thetable: " + tex_escape(caption) + r"}\\[0.4ex]")
        else:
            out.append(r"\textbf{Table \ref{" + label + r"} continued}\\[0.4ex]")
        out.append(r"\begin{tabular}{" + align + "}")
        out.append(r"\toprule")
        out.append(" & ".join(headers) + r" \\")
        out.append(r"\midrule")
        for row in chunk:
            out.append(" & ".join(row) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}")
        out.append(r"\end{center}")
    out.append(r"\normalsize")
    return "\n".join(out)


def sorted_float(rows: Iterable[Dict[str, str]], key: str, reverse: bool = True) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda row: float(row.get(key, "0") or "0"), reverse=reverse)


def row_lookup(rows: Sequence[Dict[str, str]], **kwargs: str) -> Dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in kwargs.items()):
            return row
    return {}


def short_failures(value: str) -> str:
    aliases = {
        "excessive_stretch": "stretch",
        "fixture_snag": "snag",
        "force_limit": "force",
        "energy_overshoot": "energy",
        "wrong_memory_branch": "branch",
        "occlusion_miss": "occ",
        "shape_failure": "shape",
        "unstable_fold": "fold",
    }
    parts = [part for part in value.split(";") if part]
    return ",".join(aliases.get(part, part[:8]) for part in parts)


def write_references() -> None:
    refs = r"""@article{gu2023survey,
  title={A Survey on Robotic Manipulation of Deformable Objects: Recent Advances, Open Challenges and New Frontiers},
  author={Gu, Feida and Zhou, Yanmin and Wang, Zhipeng and Jiang, Shuo and He, Bin},
  journal={arXiv preprint arXiv:2312.10419},
  year={2023},
  url={https://arxiv.org/abs/2312.10419}
}

@inproceedings{muller2007pbd,
  title={Position Based Dynamics},
  author={Muller, Matthias and Heidelberger, Bruno and Hennix, Marcus and Ratcliff, John},
  booktitle={Journal of Visual Communication and Image Representation},
  volume={18},
  pages={109--118},
  year={2007},
  doi={10.1016/j.jvcir.2007.01.005}
}

@inproceedings{sanchez2020gns,
  title={Learning to Simulate Complex Physics with Graph Networks},
  author={Sanchez-Gonzalez, Alvaro and Godwin, Jonathan and Pfaff, Tobias and Ying, Rex and Leskovec, Jure and Battaglia, Peter W.},
  booktitle={International Conference on Machine Learning},
  year={2020},
  url={https://arxiv.org/abs/2002.09405}
}

@inproceedings{li2019dpi,
  title={Learning Particle Dynamics for Manipulating Rigid Bodies, Deformable Objects, and Fluids},
  author={Li, Yunzhu and Wu, Jiajun and Tedrake, Russ and Tenenbaum, Joshua B. and Torralba, Antonio},
  booktitle={International Conference on Learning Representations},
  year={2019},
  url={https://arxiv.org/abs/1810.01566}
}

@inproceedings{shi2022robocraft,
  title={RoboCraft: Learning to See, Simulate, and Shape Elasto-Plastic Objects with Graph Networks},
  author={Shi, Haochen and Xu, Huazhe and Huang, Zhiao and Li, Yunzhu and Wu, Jiajun},
  booktitle={Robotics: Science and Systems},
  year={2022},
  url={https://arxiv.org/abs/2205.02909}
}

@inproceedings{ebert2018visualforesight,
  title={Visual Foresight: Model-Based Deep Reinforcement Learning for Vision-Based Robotic Control},
  author={Ebert, Frederik and Finn, Chelsea and Dasari, Sudeep and Xie, Annie and Lee, Alex and Levine, Sergey},
  booktitle={arXiv preprint arXiv:1812.00568},
  year={2018},
  url={https://arxiv.org/abs/1812.00568}
}

@inproceedings{finn2017deepforesight,
  title={Deep Visual Foresight for Planning Robot Motion},
  author={Finn, Chelsea and Levine, Sergey},
  booktitle={IEEE International Conference on Robotics and Automation},
  year={2017},
  doi={10.1109/ICRA.2017.7989324}
}

@inproceedings{babaeizadeh2018sv2p,
  title={Stochastic Variational Video Prediction},
  author={Babaeizadeh, Mohammad and Finn, Chelsea and Erhan, Dumitru and Campbell, Roy H. and Levine, Sergey},
  booktitle={International Conference on Learning Representations},
  year={2018},
  url={https://arxiv.org/abs/1710.11252}
}

@inproceedings{hoque2020vsf,
  title={VisuoSpatial Foresight for Multi-Step, Multi-Task Fabric Manipulation},
  author={Hoque, Ryan and Seita, Daniel and Balakrishna, Ashwin and Ganapathi, Aditya and Tanwani, Ajay Kumar and Jamali, Nawid and Yamane, Katsu and Iba, Soshi and Goldberg, Ken},
  booktitle={Robotics: Science and Systems},
  year={2020},
  url={https://arxiv.org/abs/2003.09044}
}

@inproceedings{wu2023affordance,
  title={Learning Foresightful Dense Visual Affordance for Deformable Object Manipulation},
  author={Wu, Ruihai and Ning, Chuanruo and Dong, Hao},
  booktitle={IEEE/CVF International Conference on Computer Vision},
  year={2023},
  url={https://arxiv.org/abs/2303.11057}
}

@book{rawlings2017mpc,
  title={Model Predictive Control: Theory, Computation, and Design},
  author={Rawlings, James B. and Mayne, David Q. and Diehl, Moritz M.},
  edition={2},
  publisher={Nob Hill Publishing},
  year={2017},
  url={https://sites.engineering.ucsb.edu/~jbraw/mpc/}
}

@article{doucet2001particle,
  title={An Introduction to Sequential Monte Carlo Methods},
  author={Doucet, Arnaud and de Freitas, Nando and Gordon, Neil},
  journal={Sequential Monte Carlo Methods in Practice},
  pages={3--14},
  year={2001},
  publisher={Springer}
}

@article{pedregosa2011scikit,
  title={Scikit-learn: Machine Learning in Python},
  author={Pedregosa, Fabian and Varoquaux, Gael and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and others},
  journal={Journal of Machine Learning Research},
  volume={12},
  pages={2825--2830},
  year={2011},
  url={https://jmlr.org/papers/v12/pedregosa11a.html}
}
"""
    (PAPER / "references.bib").write_text(refs, encoding="utf-8")


def manuscript() -> str:
    fields = summary_fields()
    metrics = read_csv("metrics.csv")
    seed_metrics = read_csv("raw_seed_metrics.csv")
    pairwise = read_csv("pairwise_stats.csv")
    aggregate = read_csv("aggregate_metrics.csv")
    aggregate_pairwise = read_csv("aggregate_pairwise_stats.csv")
    ablations = read_csv("ablation_metrics.csv")
    stress = read_csv("stress_sweep.csv")
    fixed = read_csv("fixed_risk_metrics.csv")
    fixed_seed_metrics = read_csv("fixed_risk_seed_metrics.csv")
    fixed_pairwise = read_csv("fixed_risk_pairwise.csv")
    negatives = read_csv("negative_cases.csv")
    training = read_csv("training_summary.csv")

    combined = [row for row in metrics if row.get("split") == "combined_memory_stress"]
    v5 = row_lookup(combined, method="action_conditioned_memory_v5")
    non_oracle = [row for row in combined if row.get("method") not in {"action_conditioned_memory_v5", "oracle_latent_state"}]
    best = sorted_float(non_oracle, "mean_success")[0] if non_oracle else {}
    main_pair = row_lookup(pairwise, split="combined_memory_stress", comparison=best.get("method", ""))
    old = row_lookup(combined, method="action_conditioned_memory")
    oracle = row_lookup(combined, method="oracle_latent_state")
    aggregate_v5 = row_lookup(aggregate, method="action_conditioned_memory_v5", split="hard_regime")
    aggregate_best = sorted_float(
        [row for row in aggregate if row.get("split") == "hard_regime" and row.get("method") not in {"action_conditioned_memory_v5", "oracle_latent_state"}],
        "mean_success",
    )[0]
    aggregate_pair = row_lookup(aggregate_pairwise, split="hard_regime", comparison=aggregate_best.get("method", ""))
    full_ablation = row_lookup(ablations, method="action_conditioned_v5_full")
    max_stress = max((float(row["stress_level"]) for row in stress), default=0.0)
    stress_max = [row for row in stress if abs(float(row.get("stress_level", "0")) - max_stress) < 1e-9]
    stress_v5 = row_lookup(stress_max, method="action_conditioned_memory_v5")
    stress_best = sorted_float([row for row in stress_max if row.get("method") not in {"action_conditioned_memory_v5", "oracle_latent_state"}], "mean_success")[0]

    main_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_memory_error", "ci95_memory_error"),
            pm(row, "mean_mechanism_macro_f1", "ci95_mechanism_macro_f1"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted(metrics, key=lambda r: (SPLIT_ALIASES.get(r["split"], r["split"]), -float(r["mean_success"])))
    ]
    combined_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_shape_error", "ci95_shape_error"),
            pm(row, "mean_memory_error", "ci95_memory_error"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_force_clip_rate", "ci95_force_clip_rate"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted_float(combined, "mean_success")
    ]
    pair_rows = [
        [
            split_tex(row["split"]),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_memory_error_reduction"]),
            f(row["paired_mechanism_f1_diff"]),
            f(row["paired_damage_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(pairwise, key=lambda r: (r["split"], r["comparison"]))
    ]
    aggregate_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_memory_error", "ci95_memory_error"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted_float(aggregate, "mean_success")
    ]
    fixed_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            f(row["risk_budget"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_force_clip_rate", "ci95_force_clip_rate"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted(fixed, key=lambda r: (r["split"], float(r["risk_budget"]), -float(r["mean_success"])))
    ]
    fixed_pair_rows = [
        [
            split_tex(row["split"]),
            f(row["risk_budget"], 2),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_damage_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(fixed_pairwise, key=lambda r: (r["split"], float(r["risk_budget"]), r["comparison"]))
    ]
    ablation_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_memory_error", "ci95_memory_error"),
            pm(row, "mean_mechanism_macro_f1", "ci95_mechanism_macro_f1"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted_float(ablations, "mean_success")
    ]
    stress_rows = [
        [
            method_tex(row["method"]),
            f(row["stress_level"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_damage_rate", "ci95_damage_rate"),
            pm(row, "mean_force_clip_rate", "ci95_force_clip_rate"),
            pm(row, "mean_diagnostic_rate", "ci95_diagnostic_rate"),
        ]
        for row in sorted(stress, key=lambda r: (float(r["stress_level"]), r["method"]))
    ]
    seed_metric_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["damage_rate"]),
            f(row["memory_error"]),
            f(row["mechanism_macro_f1"]),
            f(row["diagnostic_rate"]),
        ]
        for row in sorted(seed_metrics, key=lambda r: (r["split"], r["method"], int(r["seed"])))
    ]
    negative_rows = [
        [
            tex_escape(row.get("seed", "")),
            tex_escape(row.get("object_type", "")),
            tex_escape(row.get("chosen_action", "")),
            method_tex(row.get("successful_baseline", "")) if row.get("successful_baseline", "") else "",
            tex_escape(row.get("successful_baseline_action", "")),
            tex_escape(short_failures(row.get("actual_failures", ""))),
            f(row.get("shape_error", "0")),
        ]
        for row in negatives
    ]
    fixed_seed_metric_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            f(row["risk_budget"], 2),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["damage_rate"]),
            f(row["force_clip_rate"]),
            f(row["diagnostic_rate"]),
        ]
        for row in sorted(
            [row for row in fixed_seed_metrics if row.get("risk_budget") in {"0.10", "0.20"}],
            key=lambda r: (r["split"], float(r["risk_budget"]), r["method"], int(r["seed"])),
        )
    ]
    checklist_rows = [
        [tex_escape(name), tex_escape(status)]
        for name, status in [
            ("CPU-only execution", "all experiments use NumPy, matplotlib, scikit-learn Ridge models, and a local mass-spring simulator"),
            ("RAM-light execution", "single-process run; no checkpoints or large neural tensors"),
            ("No Desktop PDF", "final numbered PDF is copied only to Downloads"),
            ("Bright citation boxes", "hyperref uses green citation borders, orange internal links, and blue URL borders"),
            ("Frozen main split", "combined_memory_stress is the primary gate"),
            ("Frozen aggregate split", "hard_regime averages hidden_strain, occluded_contact, material_shift, and combined stress"),
            ("Frozen fixed-risk budgets", "0.10, 0.20, 0.30, and 0.40"),
            ("Oracle disclosed", "oracle_latent_state is an upper bound, not a deployable method"),
            ("Hardware limitation disclosed", "no real-robot experiments are claimed"),
            ("External benchmark limitation disclosed", "no public deformable benchmark validation is claimed"),
            ("Negative cases retained", "scenario-level failures remain in the artifact"),
            ("Ablation gate retained", "full v5 must beat its own removals"),
            ("Stress gate retained", "maximum stress is reported even when unfavorable"),
            ("Paired comparisons retained", "success differences are computed over matched seeds"),
            ("Safety reported", "damage, force clipping, contact, and diagnostics are not hidden"),
            ("No fake citations", "bibliography entries are real sources checked against primary pages"),
        ]
    ]
    train = training[0] if training else {}
    decision = fields.get("terminal_recommendation", "UNKNOWN")
    reason = fields.get("reason", "")
    negative_table = chunked_table(
        "Scenario-level negative cases for v5.",
        "tab:negative",
        ["seed", "object", "v5 action", "successful baseline", "baseline action", "failures", "shape"],
        "lllllp{0.24\\linewidth}c",
        negative_rows,
        chunk_size=18,
        size="\\tiny",
    )
    seed_metric_table = chunked_table(
        "Per-seed main metrics.",
        "tab:seed-main",
        ["method", "split", "seed", "n", "success", "damage", "mem err", "F1", "diag"],
        "llccccccc",
        seed_metric_rows,
        chunk_size=30,
        size="\\tiny",
    )
    checklist_table = chunked_table(
        "Artifact and reproducibility checklist.",
        "tab:checklist",
        ["item", "status"],
        "p{0.25\\linewidth}p{0.66\\linewidth}",
        checklist_rows,
        chunk_size=16,
        size="\\footnotesize",
    )
    fixed_seed_metric_table = chunked_table(
        "Per-seed fixed-risk metrics at the two decisive budgets.",
        "tab:fixed-seed",
        ["method", "split", "budget", "seed", "n", "success", "damage", "clip", "diag"],
        "llccccccc",
        fixed_seed_metric_rows,
        chunk_size=30,
        size="\\tiny",
    )

    text = rf"""
\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{url}}
\usepackage[colorlinks=false,pdfborder={{0 0 1.6}},citebordercolor={{0 1 0}},linkbordercolor={{1 0.55 0}},urlbordercolor={{0 0.45 1}}]{{hyperref}}
\usepackage{{natbib}}

\title{{Action-Conditioned Deformable Memory Still Fails as a Closed-Loop Manipulation Claim}}
\author{{Anonymous Authors}}

\begin{{document}}
\maketitle

\begin{{abstract}}
We rebuild a generated deformable-manipulation idea into an expanded, CPU-only, evidence-bearing ICLR-style artifact. The hypothesis is attractive: visually similar ropes, cloth strips, elastic bands, and sheets can carry different latent strain, contact, crease, or stored-energy histories, so a robot should preserve action-conditioned hidden material memory rather than plan only from current visible geometry. The v5 rebuild makes the claim as strong as we can without inventing evidence: it adds a safety-gated action-conditioned memory planner, stronger damage-aware and risk-constrained baselines, an aggregate hard-regime analysis, fixed-risk evaluation, ablations, stress sweeps, negative cases, and a 25-page reproducibility-focused manuscript. The result remains a negative result under the frozen gates. On the decisive \texttt{{combined\_memory\_stress}} split, \texttt{{ACM-v5}} reaches {pm(v5, "mean_success", "ci95_success") if v5 else "N/A"} success while the strongest non-oracle baseline, {method_tex(best.get("method", "")) if best else "N/A"}, reaches {pm(best, "mean_success", "ci95_success") if best else "N/A"}. The paired v5-minus-baseline success difference is ${f(main_pair.get("paired_success_diff", "0"))} \pm {f(main_pair.get("ci95_success_diff", "0"))}$. We therefore mark the paper \textbf{{{tex_escape(decision)}}}: hidden memory can improve diagnostics, but the current planner does not convert that memory into a robust and safe manipulation advantage.
\end{{abstract}}

\section{{Decision And Claim}}
This paper is intentionally written as a submission-hardening document rather than as a celebratory benchmark paper. The submitted claim would be that action-conditioned hidden deformable memory improves downstream manipulation under partial observation and material/contact ambiguity. That claim is only credible if it survives the strongest visible-state, graph, particle-filter, ensemble, robust surrogate, and safety-aware baselines. It does not. The terminal decision emitted by the frozen runner is \textbf{{{tex_escape(decision)}}}. The exact machine-readable reason is:

\begin{{quote}}\small
{tex_escape(reason)}
\end{{quote}}

The important distinction is between \emph{{state estimation}} and \emph{{control}}. Prior work makes the modeling pressure clear: deformable manipulation is difficult because the state is high-dimensional, partially observed, history-dependent, and contact-rich \citep{{gu2023survey,muller2007pbd}}. Learned graph and particle simulators are strong prior art for representing such systems \citep{{sanchez2020gns,li2019dpi,shi2022robocraft}}. Visual MPC and foresight work shows that action-conditioned prediction can be useful for manipulation \citep{{finn2017deepforesight,ebert2018visualforesight,hoque2020vsf}}. The present question is narrower and harsher: does preserving hidden deformable memory improve closed-loop control when diagnostic actions can themselves damage the object?

\section{{Frozen Submission Gates}}
The plan froze the following gates before the full v5 run. A promotion above archive requires all of them:
\begin{{itemize}}
\item v5 must beat the strongest non-oracle baseline on \texttt{{combined\_memory\_stress}} by at least 0.04 mean success.
\item The paired lower bound against that baseline must be positive on the combined split.
\item The paired lower bound must also be positive on the aggregate hard regime.
\item v5 must be best or tied-best under fixed predicted-risk budgets 0.10 and 0.20.
\item v5 must not increase damage or force clipping relative to the strongest baseline.
\item v5 must show that hidden-memory or mechanism improvements translate into downstream success.
\item No ablation may match or beat the full v5 method on primary success within tolerance.
\item Maximum-stress behavior must not collapse earlier than the strongest non-oracle baseline.
\end{{itemize}}

\section{{Benchmark}}
The benchmark is a local two-dimensional mass-spring deformable simulator. Each scenario instantiates one of four object families: rope, cloth strip, elastic band, or deformable sheet. The simulator includes spring rest-length memory, damping, friction, material shift, fixture contact, force clipping, partial observation, hidden strain/contact memory, and a target-shape objective. This is not a substitute for hardware or for a public benchmark; it is a controlled diagnostic environment designed to test whether the claim deserves more expensive validation.

The five splits are \texttt{{nominal\_visible\_state}}, \texttt{{hidden\_strain\_memory}}, \texttt{{occluded\_contact\_memory}}, \texttt{{material\_shift}}, and \texttt{{combined\_memory\_stress}}. The hard-regime aggregate averages hidden strain, occluded contact, material shift, and combined stress. The full run uses {tex_escape(train.get("seed_count", "?"))} seeds, {tex_escape(train.get("train_scenarios_per_split", "?"))} training scenarios per split, {tex_escape(train.get("eval_scenarios_per_split", "?"))} evaluation scenarios per split, {tex_escape(train.get("stress_scenarios", "?"))} stress scenarios, {tex_escape(train.get("fixed_risk_scenarios", "?"))} fixed-risk scenarios, {tex_escape(train.get("actions", "?"))} discrete actions, and {tex_escape(train.get("sim_steps", "?"))} integration steps per rollout.

\section{{Methods}}
The implemented methods are deliberately stronger than the original generated idea. \texttt{{visible\_state\_mpc}} plans from observed/imputed keypoints only. \texttt{{damage\_aware\_visible\_mpc}} is a stronger visible-state baseline with conservative contact and force penalties. \texttt{{history\_rnn\_estimator}} is a CPU-light history-feature estimator. \texttt{{particle\_filter\_memory}} maintains multiple latent hypotheses. \texttt{{safety\_constrained\_particle\_filter}} makes that particle baseline conservative under predicted damage. \texttt{{graph\_dynamics\_baseline}} uses graph-style shape and edge features. \texttt{{ensemble\_uncertainty\_planner}} plans over bootstrap uncertainty. \texttt{{robust\_cem\_surrogate}} is a conservative surrogate planner inspired by model-predictive action search \citep{{rawlings2017mpc}}. \texttt{{action\_conditioned\_memory}} is the v4 proposal. \texttt{{action\_conditioned\_memory\_v5}} is the strongest proposed variant: it blends action, history, and graph estimates; preserves branch memory; penalizes damage; gates diagnostic actions; and uses conservative scoring across latent hypotheses. \texttt{{oracle\_latent\_state}} is a nondeployable upper bound.

\section{{Why Memory Can Fail}}
\paragraph{{Definition.}} Let $x_t$ be the visible deformable configuration, $m_t$ be latent material memory, and $a_t$ be a manipulation action. A memory estimator is useful for control only if the policy class contains actions whose expected value under $p(m_t \mid x_{{\leq t}}, a_{{<t}})$ exceeds the value of robust visible-state actions.

\paragraph{{Proposition.}} Suppose diagnostic actions reduce latent entropy but have damage probability $\delta > 0$, and suppose the candidate action library has no low-risk diagnostic alternative for a subset of states with mass $\rho$. Then a policy that prefers diagnostics whenever uncertainty is high can reduce memory error while decreasing task success whenever $\rho\delta$ exceeds the downstream value of the information gained. This is the failure pattern v4 exposed and v5 attempts to repair.

\paragraph{{Empirical implication.}} The paper cannot claim success by showing lower memory error alone. It must show success, safety, fixed-risk robustness, and ablation necessity. This is why the frozen gates treat hidden-memory error and mechanism F1 as secondary metrics.

\section{{Main Results}}
{figure("deformable_memory_final_success.png", "Combined-memory-stress success. The proposed v5 method is compared with stronger visible, particle, graph, ensemble, robust-surrogate, v4, and oracle baselines.")}
{figure("deformable_memory_damage_rate.png", "Combined-memory-stress damage. Safety is a primary quantity, not an appendix-only diagnostic.")}

Table~\ref{{tab:combined}} reports the decisive split. The oracle row shows whether the action library and simulator can solve the split when full hidden state is available. The gap between oracle and non-oracle methods is real, but the v5 method must beat deployable baselines, not the lower bound implied by v4.

{chunked_table("Combined-memory-stress summary.", "tab:combined", ["method", "success", "shape", "mem err", "damage", "clip", "diag"], "lcccccc", combined_rows, chunk_size=18)}

The strongest non-oracle baseline on the decisive split is {method_tex(best.get("method", ""))}. The paired v5-minus-baseline difference is ${f(main_pair.get("paired_success_diff", "0"))} \pm {f(main_pair.get("ci95_success_diff", "0"))}$, with memory-error reduction ${f(main_pair.get("paired_memory_error_reduction", "0"))}$, mechanism-F1 difference ${f(main_pair.get("paired_mechanism_f1_diff", "0"))}$, and damage reduction ${f(main_pair.get("paired_damage_reduction", "0"))}$. The v4 row is also included: \texttt{{ACM-v4}} reaches {pm(old, "mean_success", "ci95_success") if old else "N/A"} success and {pm(old, "mean_damage_rate", "ci95_damage_rate") if old else "N/A"} damage, showing why the safety-gated v5 method was necessary even if it still fails the full submission gate.

\section{{Aggregate Hard-Regime Evidence}}
The aggregate hard regime is a guard against overfitting a single split. It averages hidden strain, occluded contact, material shift, and combined memory stress at seed level. \texttt{{ACM-v5}} reaches {pm(aggregate_v5, "mean_success", "ci95_success") if aggregate_v5 else "N/A"} aggregate success. The best non-oracle aggregate baseline is {method_tex(aggregate_best.get("method", ""))}, and the paired aggregate difference is ${f(aggregate_pair.get("paired_success_diff", "0"))} \pm {f(aggregate_pair.get("ci95_success_diff", "0"))}$. This is the second hard gate.

{chunked_table("Aggregate hard-regime metrics.", "tab:aggregate", ["method", "success", "mem err", "damage", "diag"], "lcccc", aggregate_rows, chunk_size=18)}

\section{{Fixed-Risk Evaluation}}
{figure("deformable_memory_fixed_risk.png", "Fixed-risk success on the combined split. Methods are replanned under predicted-risk budgets rather than unconstrained surrogate scores.")}

Fixed-risk evaluation asks whether a method can maintain success when predicted manipulation risk is capped. This matters because deformable objects often fail by a small number of high-energy, high-contact actions. If memory only wins by taking dangerous probes, it is not a usable robotics result.

{chunked_table("Fixed-risk summary across hard splits and risk budgets.", "tab:fixed", ["method", "split", "budget", "success", "damage", "clip", "diag"], "llccccc", fixed_rows, chunk_size=26)}

\section{{Ablations}}
The ablations remove action conditioning, branch memory, safety gates, diagnostic gates, damage penalties, material memory, and uncertainty terms from the v5 planner. The ablation gate is intentionally strict: if an ablation matches full v5, the claimed mechanism is not necessary. Full v5 reaches {pm(full_ablation, "mean_success", "ci95_success") if full_ablation else "N/A"} success.

{figure("deformable_memory_ablation_success.png", "Ablation success for v5 components on combined memory stress.")}
{chunked_table("V5 ablations.", "tab:ablation", ["ablation", "success", "damage", "mem err", "mech F1", "diag"], "lccccc", ablation_rows, chunk_size=18)}

\section{{Stress Sweep}}
{figure("deformable_memory_stress_sweep.png", "Stress sweep over combined hidden strain, occlusion, material shift, fixture strength, force limits, and observation noise.")}

At maximum stress level {f(max_stress, 2)}, \texttt{{ACM-v5}} reaches {pm(stress_v5, "mean_success", "ci95_success") if stress_v5 else "N/A"} success, while the strongest non-oracle stress baseline, {method_tex(stress_best.get("method", ""))}, reaches {pm(stress_best, "mean_success", "ci95_success") if stress_best else "N/A"}. This gate is reported even if it is unfavorable.

{chunked_table("Stress sweep metrics.", "tab:stress", ["method", "level", "success", "damage", "clip", "diag"], "lccccc", stress_rows, chunk_size=28)}

\section{{Negative Cases}}
Negative cases are not anecdotes used to excuse the result; they are scenario-level checks that the average tables do not hide systematic failure modes. When a successful non-oracle baseline exists on the same scenario, the table lists it.

{negative_table}

\section{{Limitations}}
This artifact is not a real-robot paper. It has no hardware videos, no public deformable benchmark, no tactile sensing, no RGBD perception stack, and no large neural dynamics model. It uses Ridge regressors from scikit-learn \citep{{pedregosa2011scikit}} and a local simulator so that the evidence is cheap, reproducible, and easy to audit. Those constraints are deliberate, but they limit external validity. The right conclusion is not that deformable memory is useless; it is that this specific action-conditioned memory planner is not yet a submission-worthy control result.

\section{{Conclusion}}
The v5 rebuild improves the scientific artifact and sharpens the negative result. It adds the theory that v4 was missing, tries the obvious safety-gated rescue, evaluates stronger baselines, reports fixed-risk and stress behavior, and preserves failures. The frozen decision remains \textbf{{{tex_escape(decision)}}}. A future revival would need either safer diagnostic actions, a richer low-risk action library, hardware validation, or a learned dynamics model that turns hidden memory into a consistent closed-loop advantage.

\clearpage
\appendix
\section{{Full Main Metrics}}
{chunked_table("All method/split main metrics.", "tab:main-all", ["method", "split", "success", "damage", "mem err", "mech F1", "diag"], "llccccc", main_rows, chunk_size=24)}

\section{{Full Pairwise Comparisons}}
{chunked_table("Pairwise v5-minus-comparison statistics by split.", "tab:pairwise", ["split", "comparison", "d success", "CI", "mem red", "F1 diff", "dmg red", "better"], "llcccccc", pair_rows, chunk_size=24)}

\section{{Fixed-Risk Pairwise Comparisons}}
{chunked_table("Fixed-risk pairwise comparisons.", "tab:fixed-pair", ["split", "budget", "comparison", "d success", "CI", "dmg red", "better"], "llccccc", fixed_pair_rows, chunk_size=24)}

\section{{Per-Seed Main Metrics}}
Paired statistics are only meaningful if the seed-level evidence is available. Table~\ref{{tab:seed-main}} therefore includes the per-seed, per-method, per-split summaries used to compute the main confidence intervals and pairwise differences.

{seed_metric_table}

\section{{Per-Seed Fixed-Risk Metrics}}
The fixed-risk gate is decisive for this paper because v5 improves latent-memory proxies but can still fail safety. Table~\ref{{tab:fixed-seed}} includes seed-level fixed-risk evidence for the two frozen promotion budgets, 0.10 and 0.20.

{fixed_seed_metric_table}

\section{{Reproducibility Checklist}}
{checklist_table}

\section{{Protocol Notes}}
The simulator is intentionally small enough to rerun on CPU. Each rollout records seed, scenario, split, object type, chosen action, true and estimated memory, uncertainty, visible fraction, success, shape error, memory error, damage, stretch, contact, force clipping, strain energy, progress, diagnostic count, actual failures, predicted failures, and a compact trajectory trace. The raw rollout file is not typeset in full because it is thousands of rows, but the seed-level aggregates, fixed-risk aggregates, stress aggregates, ablations, pairwise statistics, and negative cases are included above. The code path that produced the paper is:
\begin{{verbatim}}
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
\end{{verbatim}}

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}
\end{{document}}
"""
    text = re.sub(r"\n{3,}", "\n\n", text.strip() + "\n")
    return text


def main() -> None:
    PAPER.mkdir(exist_ok=True)
    write_references()
    (PAPER / "main.tex").write_text(manuscript(), encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'} and {PAPER / 'references.bib'}")


if __name__ == "__main__":
    main()
