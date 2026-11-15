"""Visualisation du monde 2D : rejoue pas à pas une des populations mesurées.

    python experiments/monde_dechet/voir.py [--regime saisons]

Écrit ``out/monde_2d_<régime>_pop0.html`` (un fichier par cas).

Resimule la population 0 du régime espace (même graine que ``run.py``), enregistre
trois scènes de 300 pas et les insère dans ``voir.html``, une page autonome à ouvrir
dans un navigateur. Si ``run.py`` a déjà tourné, vérifie que la population finale est
bien celle qui a été mesurée.
"""

from __future__ import annotations

import argparse
import base64
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
from commun import ESPACE, naissance
from motifs import motif

from simsbn.milieu import ARCH, step_brains
from simsbn.monde import Vie
from simsbn.structure import KINDS, Classifier

HERE = Path(__file__).parent
RESERVE = HERE.parent / "saisons_reserve" / "run.py"
DIRECTIONS = HERE.parent / "directions" / "run.py"
FONDATEUR = HERE.parent / "fondateur"
SAISONS_DIR = HERE.parent / "saisons_directions" / "run.py"
RATES = (0.0, 0.1, 0.3, 1.0)  # ceux de experiments/fondateur/run.py
SCENES = [("Départ", 0), ("Pas 2 000", 2_000), ("Fin", 19_700)]  # (nom, pas de départ)
# Octet d'état d'un agent : ce qu'il a fait pendant le pas, et ce qui lui est arrivé.
SENSOR, EAT, MOVE, HIDDEN, BORN, FED, POISONED = (1 << k for k in range(7))


def encode(values, dtype) -> str:
    return base64.b64encode(np.asarray(values, dtype=dtype).tobytes()).decode("ascii")


def record(vie, frames: int, classify: Classifier) -> dict:
    """Avance ``vie`` de ``frames`` pas et renvoie la scène, prête pour le JSON."""
    monde = vie.monde
    grid = np.zeros((frames, monde.cells), dtype=np.uint8)
    counts, index, cell, state, energy = [], [], [], [], []
    local: dict[int, int] = {}  # numéro d'agent -> rang dans la scène
    agents, genotypes, matrices = [], {}, []
    summer, pre = [], []
    for f in range(frames):
        before = dict(zip(vie.ident.tolist(), vie.brain.tolist(), strict=True))
        summer.append(int(monde.is_summer(vie.t)))
        motors = vie.corps.motors
        if motors:  # actions portées par les moteurs : ce qu'ils valaient au début du pas
            eat_j = motors.index("ingérer")
            ways = [j for j, name in enumerate(motors) if name != "ingérer"]
            acted = {
                ident: (int(row[eat_j]), 0, int(any(row[j] for j in ways)))
                for ident, row in zip(vie.ident.tolist(), vie.motor.tolist(), strict=True)
            }
        else:
            acted = dict(zip(vie.ident.tolist(), vie.brain.tolist(), strict=True))
        vie.step()
        grid[f] = np.minimum(vie.food, 7) | (np.minimum(vie.waste, 31) << 3)
        counts.append(len(vie))
        for k, ident in enumerate(vie.ident.tolist()):
            if ident not in local:
                key = tuple(vie.population[k][: ARCH.d, 1:].ravel().tolist())
                if key not in genotypes:
                    genotypes[key] = len(genotypes)
                    matrices.append(vie.population[k])
                local[ident] = len(agents)
                agents.append((ident, int(vie.lineage[k]), genotypes[key]))
            bits = SENSOR * int(vie.sensor[k])
            if ident in acted:
                e, m, h = acted[ident]
                if motors:  # déplacement net : nord et sud allumés ensemble s'annulent
                    m = int(vie.last_delta[k].any())
                bits |= EAT * e | MOVE * m | HIDDEN * h
            else:
                bits |= BORN
            bits |= FED * int(vie.fed[k]) | POISONED * int(vie.poisoned[k])
            # état du cerveau avant le pas (bits 0 à 2), et bit 3 si l'agent existait déjà
            b = before.get(ident) if ident in acted else None
            pre.append(8 | b[0] | b[1] << 1 | b[2] << 2 if b else 0)
            index.append(local[ident])
            state.append(bits)
        # contrôle : rejouer les pas d'agent depuis l'état d'avant redonne l'état d'après
        old = np.flatnonzero([i in before and i in acted for i in vie.ident.tolist()])
        x = np.array([before[i] for i in vie.ident[old].tolist()]).reshape(-1, ARCH.n_brain)
        for _ in range(vie.corps.ticks):
            x = step_brains(vie.population[old], vie.sensor[old], x)
        assert np.array_equal(x, vie.brain[old]), "trajet du cerveau incohérent"
        cell.extend(vie.cell.tolist())
        energy.extend(vie.energy.tolist())
    matrices = np.array(matrices)
    return {
        "frames": frames,
        "grid": encode(grid, np.uint8),
        "counts": counts,
        "summer": summer,
        "index": encode(index, "<u2"),
        "cell": encode(cell, "<u2"),
        "state": encode(state, np.uint8),
        "energy": encode(energy, np.uint8),
        "pre": encode(pre, np.uint8),
        "ident": [a[0] for a in agents],
        "lineage": [a[1] for a in agents],
        "genotype": [a[2] for a in agents],
        "weights": [list(key) for key in genotypes],
        "flags": classify.flags(matrices[:, : ARCH.d, : ARCH.d]).astype(int).tolist(),
        "motifs": None if motors else [[motif(W, 0), motif(W, 1)] for W in matrices],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--regime",
        choices=("espace", "saisons", "directions", "fondateur", "saisons-directions"),
        default="espace",
        help="espace : monde à déchet ; saisons : saisons cachées ; directions : cinq moteurs ; "
        "fondateur : cinq moteurs, 300 clones au départ",
    )
    parser.add_argument("--mu", type=float, default=0.3, choices=RATES,
                        help="mutations par naissance (régime fondateur)")  # fmt: skip
    parser.add_argument("--replicate", type=int, default=0, help="population du régime choisi")
    parser.add_argument("--frames", type=int, default=300, help="pas enregistrés par scène")
    parser.add_argument("--steps", type=int, default=20_000, help="durée de l'expérience rejouée")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    nodes = ["capteur", "ingérer", "bouger", "caché"]
    expected = None  # effectif final relevé par l'expérience, quand la population n'est pas gardée
    if args.regime == "fondateur":
        spec = importlib.util.spec_from_file_location("directions_run", DIRECTIONS)
        directions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(directions)
        monde, corps = directions.ESPACE, directions.CORPS
        founder = np.load(FONDATEUR / "out" / "fondateur.npy")
        # même flux que experiments/fondateur/run.py, régime « directions »
        rng = np.random.default_rng([args.seed, 7, 2, 0, RATES.index(args.mu), args.replicate])
        clones = np.repeat(founder[None], 300, axis=0)
        vie = Vie(clones, monde, rng, args.mu, directions.BOUND, corps)
        measured_path = FONDATEUR / "out" / "absent.npz"
        nodes = ["capteur", "c1", "c2", "c3", *corps.motors]
        series = FONDATEUR / "out" / "fondateur_unique.csv"
        if series.exists():
            with open(series) as handle:
                for row in csv.DictReader(handle):
                    if (row["regime"], float(row["mu"]), int(row["replicate"]), row["step"]) == (
                        "directions", args.mu, args.replicate, "20000"):  # fmt: skip
                        expected = int(float(row["effectif"]))
    elif args.regime == "saisons-directions":
        spec = importlib.util.spec_from_file_location("saisons_directions_run", SAISONS_DIR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        monde, corps = module.SAISONS, module.CORPS
        rng = np.random.default_rng([args.seed, args.replicate, 0, 8])  # régime « saisons »
        args.mu = 0.5
        pop = corps.arch.random(rng, 300, module.BOUND)
        vie = Vie(pop, monde, rng, args.mu, module.BOUND, corps)
        measured_path = SAISONS_DIR.parent / "out" / "absent.npz"
        nodes = ["capteur", "c1", "c2", "c3", *corps.motors]
        series = SAISONS_DIR.parent / "out" / "saisons_directions.csv"
        if series.exists():
            with open(series) as handle:
                for row in csv.DictReader(handle):
                    if (row["regime"], int(row["replicate"]), row["year"]) == (
                        "saisons", args.replicate, str(args.steps // 100 - 1)):  # fmt: skip
                        expected = int(float(row["effectif_hiver"]))
    elif args.regime == "directions":
        spec = importlib.util.spec_from_file_location("directions_run", DIRECTIONS)
        directions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(directions)
        monde = directions.REGIMES["directions"][0]
        corps = directions.CORPS
        rng = np.random.default_rng(
            [args.seed, args.replicate, list(directions.REGIMES).index("directions"), 6]
        )
        pop = corps.arch.random(rng, 300, directions.BOUND)
        vie = Vie(pop, monde, rng, 0.1, directions.BOUND, corps)
        measured_path = DIRECTIONS.parent / "out" / "populations_finales.npz"
        measured_key = f"directions_{args.replicate}"
        nodes = ["capteur", "c1", "c2", "c3", *corps.motors]
    elif args.regime == "saisons":
        spec = importlib.util.spec_from_file_location("saisons_reserve_run", RESERVE)
        reserve = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reserve)
        monde = reserve.REGIMES["saisons"][0]
        rng = np.random.default_rng(
            [args.seed, args.replicate, list(reserve.REGIMES).index("saisons"), 4]
        )
        vie = Vie(ARCH.random(rng, 300, reserve.BOUND), monde, rng, 0.1, reserve.BOUND)
        measured_path = RESERVE.parent / "out" / "populations_finales.npz"
        measured_key = f"saisons_{args.replicate}"
    else:
        monde = ESPACE
        vie = naissance("espace", args.replicate, args.seed)
        measured_path = HERE / "out" / "populations_finales.npz"
        measured_key = f"espace_{args.replicate}"
    classify = Classifier()
    scenes = []
    scenes_plan = list(SCENES)
    if args.steps > 20_000:  # simulation prolongée : le milieu et la fin en plus
        half = args.steps // 2
        scenes_plan[-1] = ("Pas 19 700", 19_700)
        scenes_plan += [(f"Pas {half:,}".replace(",", " "), half), ("Fin", args.steps - 300)]
    for name, start in scenes_plan:
        while vie.t < start:
            vie.step()
        scene = record(vie, args.frames, classify)
        scenes.append({"name": name, "start": start + 1, **scene})
        print(f"scène « {name} » : pas {start + 1} à {vie.t}, {len(scene['ident'])} agents")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    if measured_path.exists() and vie.t == 20_000 == args.steps:
        same = np.array_equal(np.load(measured_path)[measured_key], vie.population)
        print("population finale identique à celle mesurée par run.py :", "oui" if same else "NON")
        if not same:
            raise SystemExit("la population rejouée n'est pas celle de l'expérience")

    if expected is not None and vie.t == args.steps:
        print(f"effectif final {len(vie)}, relevé par run.py : {expected}")
        if len(vie) != expected:
            raise SystemExit("la population rejouée n'est pas celle de l'expérience")

    data = {
        "regime": args.regime,
        "mu": args.mu,
        "height": monde.height,
        "width": monde.width,
        "food_cap": monde.food_cap,
        "tox": monde.tox,
        "divide_at": monde.divide_at,
        "summer": monde.summer,
        "winter": monde.winter,
        "replicate": args.replicate,
        "seed": args.seed,
        "nodes": nodes,
        "ncols": len(nodes) - 1,
        "kinds": KINDS,
        "brain": ARCH.n_brain,
        "ticks": vie.corps.ticks,
        "scenes": scenes,
    }
    page = (HERE / "voir.html").read_text(encoding="utf-8")
    marker = "/*DONNEES*/null"
    assert page.count(marker) == 1
    suffix = f"_mu{args.mu:g}" if args.regime == "fondateur" else ""
    if args.steps != 20_000:
        suffix += f"_{args.steps}pas"
    path = out / f"monde_2d_{args.regime}{suffix}_pop{args.replicate}.html"  # un fichier par cas
    path.write_text(page.replace(marker, json.dumps(data, separators=(",", ":"))), encoding="utf-8")
    print(f"page : {path} ({path.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
