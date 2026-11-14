"""Analyse après coup des populations finales du monde à déchet (non prévue au protocole).

    python experiments/monde_dechet/motifs.py    # lit out/populations_finales.npz

1. Motif du nœud de déplacement dans chaque contexte : allumé, éteint ou oscillant.
2. Signe des poids du capteur et scission SBN.
3. Agents construits à la main : rester tant que tout va bien (réactif) contre rester
   un seul pas (alternant), avec et sans poison.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
from commun import ESPACE, REGIMES

from simsbn.milieu import step_brains
from simsbn.monde import ALTERNANT, EAT, MARCHEUR, MOVE, REACTIF, Vie
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier

TARGET = ("allumé", "oscille")  # capteur 0, capteur 1


def motif(W: np.ndarray, sensor: int) -> str:
    """Valeur du nœud de déplacement sur les attracteurs atteints, ingestion allumée.

    Le capteur est tenu à ``sensor`` ; on part des 4 états du cerveau où le nœud
    d'ingestion est allumé. « variable » : la réponse dépend de l'état de départ.
    """
    kinds = set()
    for start in range(8):
        brain = np.array([[(start >> i) & 1 for i in range(3)]])
        if not brain[0, EAT]:
            continue
        seen = []
        while tuple(brain[0]) not in seen:
            seen.append(tuple(brain[0]))
            brain = step_brains(W[None], np.array([sensor]), brain)
        moves = {state[MOVE] for state in seen[seen.index(tuple(brain[0])) :]}
        kinds.add("oscille" if len(moves) == 2 else ("allumé" if moves == {1} else "éteint"))
    return kinds.pop() if len(kinds) == 1 else "variable"


def main():
    out = Path(__file__).parent / "out"
    finals = np.load(out / "populations_finales.npz")
    populations = {
        regime: [finals[f"{regime}_{r}"] for r in range(len(finals.files) // len(REGIMES))]
        for regime in REGIMES
    }
    rng = np.random.default_rng(0)

    print("1. Déplacement selon le contexte (capteur 0, capteur 1), part moyenne des agents")
    target = {}
    for regime, pops in populations.items():
        tallies = []
        for p in pops:
            genotypes, counts = np.unique(p.reshape(len(p), -1), axis=0, return_counts=True)
            tally: dict[tuple[str, str], float] = {}
            for g, n in zip(genotypes, counts, strict=True):
                key = (motif(g.reshape(4, 4), 0), motif(g.reshape(4, 4), 1))
                tally[key] = tally.get(key, 0) + n / len(p)
            tallies.append(tally)
        keys = {k for t in tallies for k in t}
        mean = {k: np.mean([t.get(k, 0) for t in tallies]) for k in keys}
        target[regime] = np.array([t.get(TARGET, 0) for t in tallies])
        print(f"   régime {regime}")
        for k in sorted(keys, key=lambda k: -mean[k])[:4]:
            major = sum(t.get(k, 0) > 0.5 for t in tallies)
            print(f"      {k[0]:9} {k[1]:9} {100 * mean[k]:5.1f} %   majoritaire dans {major}/24")
    p = permutation_test(target["espace"], target["neutre"], rng)
    print(
        f"   motif « {TARGET[0]}, {TARGET[1]} » : espace {100 * target['espace'].mean():.1f} %, "
        f"neutre {100 * target['neutre'].mean():.1f} %, p {format_p(p, sign=True)}"
    )

    print("\n2. Poids du capteur et scission SBN, part moyenne des agents")
    classify = Classifier()
    for regime, pops in populations.items():
        rows = []
        for p in pops:
            no_positive = (p[:, 0, 1:] <= 0).all(axis=1)
            scission = classify.flags(p)[:, KINDS.index("scission_sbn")]
            rows.append([no_positive.mean(), scission.mean(), (scission & ~no_positive).mean()])
        a, b, c = 100 * np.mean(rows, axis=0)
        print(
            f"   régime {regime:8} aucun poids du capteur positif {a:5.1f} %   "
            f"scission SBN {b:5.1f} %   scission avec un poids positif {c:.1f} %"
        )

    print("\n3. Réactif, alternant et marcheur mélangés (8 populations, 6 000 pas, sans mutation)")
    types = [REACTIF, ALTERNANT, MARCHEUR]
    for label, monde in (("avec poison", ESPACE), ("sans poison", replace(ESPACE, tox=np.inf))):
        shares = []
        for r in range(8):
            genotypes = np.concatenate([np.stack([g] * 150) for g in types])
            vie = Vie(genotypes, monde, np.random.default_rng([1, r]), mutation_rate=0.0)
            vie.brain[:] = (1, 0, 0)
            for _ in range(6000):
                vie.step()
            shares.append(np.bincount(vie.lineage // 150, minlength=3) / len(vie))
        a, b, c = 100 * np.mean(shares, axis=0)
        print(f"   {label} : réactif {a:.0f} %, alternant {b:.0f} %, marcheur {c:.0f} %")


if __name__ == "__main__":
    main()
