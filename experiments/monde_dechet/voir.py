"""Visualisation du monde 2D : rejoue pas à pas une des populations mesurées.

    python experiments/monde_dechet/voir.py    # écrit out/monde_2d.html

Resimule la population 0 du régime espace (même graine que ``run.py``), enregistre
trois scènes de 300 pas et les insère dans ``voir.html``, une page autonome à ouvrir
dans un navigateur. Si ``run.py`` a déjà tourné, vérifie que la population finale est
bien celle qui a été mesurée.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

import numpy as np
from commun import ESPACE, naissance
from motifs import motif

from simsbn.milieu import ARCH
from simsbn.structure import KINDS, Classifier

HERE = Path(__file__).parent
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
    for f in range(frames):
        acted = dict(zip(vie.ident.tolist(), vie.brain.tolist(), strict=True))
        vie.step()
        grid[f] = np.minimum(vie.food, 7) | (np.minimum(vie.waste, 31) << 3)
        counts.append(len(vie))
        for k, ident in enumerate(vie.ident.tolist()):
            if ident not in local:
                key = tuple(vie.population[k][:, 1:].ravel().tolist())
                if key not in genotypes:
                    genotypes[key] = len(genotypes)
                    matrices.append(vie.population[k])
                local[ident] = len(agents)
                agents.append((ident, int(vie.lineage[k]), genotypes[key]))
            bits = SENSOR * int(vie.sensor[k])
            if ident in acted:
                e, m, h = acted[ident]
                bits |= EAT * e | MOVE * m | HIDDEN * h
            else:
                bits |= BORN
            bits |= FED * int(vie.fed[k]) | POISONED * int(vie.poisoned[k])
            index.append(local[ident])
            state.append(bits)
        cell.extend(vie.cell.tolist())
        energy.extend(vie.energy.tolist())
    matrices = np.array(matrices)
    return {
        "frames": frames,
        "grid": encode(grid, np.uint8),
        "counts": counts,
        "index": encode(index, "<u2"),
        "cell": encode(cell, "<u2"),
        "state": encode(state, np.uint8),
        "energy": encode(energy, np.uint8),
        "ident": [a[0] for a in agents],
        "lineage": [a[1] for a in agents],
        "genotype": [a[2] for a in agents],
        "weights": [list(key) for key in genotypes],
        "flags": classify.flags(matrices).astype(int).tolist(),
        "motifs": [[motif(W, 0), motif(W, 1)] for W in matrices],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--replicate", type=int, default=0, help="population du régime espace")
    parser.add_argument("--frames", type=int, default=300, help="pas enregistrés par scène")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    vie = naissance("espace", args.replicate, args.seed)
    classify = Classifier()
    scenes = []
    for name, start in SCENES:
        while vie.t < start:
            vie.step()
        scene = record(vie, args.frames, classify)
        scenes.append({"name": name, "start": start + 1, **scene})
        print(f"scène « {name} » : pas {start + 1} à {vie.t}, {len(scene['ident'])} agents")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    measured = out / "populations_finales.npz"
    if measured.exists() and vie.t == 20_000:
        same = np.array_equal(np.load(measured)[f"espace_{args.replicate}"], vie.population)
        print("population finale identique à celle mesurée par run.py :", "oui" if same else "NON")
        if not same:
            raise SystemExit("la population rejouée n'est pas celle de l'expérience")

    data = {
        "height": ESPACE.height,
        "width": ESPACE.width,
        "food_cap": ESPACE.food_cap,
        "tox": ESPACE.tox,
        "replicate": args.replicate,
        "seed": args.seed,
        "nodes": ["capteur", "ingérer", "bouger", "caché"],
        "kinds": KINDS,
        "brain": ARCH.n_brain,
        "scenes": scenes,
    }
    page = (HERE / "voir.html").read_text(encoding="utf-8")
    marker = "/*DONNEES*/null"
    assert page.count(marker) == 1
    path = out / "monde_2d.html"
    path.write_text(page.replace(marker, json.dumps(data, separators=(",", ":"))), encoding="utf-8")
    print(f"page : {path} ({path.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
