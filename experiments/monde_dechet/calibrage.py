"""Calibrage du monde à déchet, avec des agents construits à la main seulement.

    python experiments/monde_dechet/calibrage.py

Ne regarde que la démographie : effectif, renouvellement, et qui l'emporte quand on
mélange immobiles, marcheurs et réactifs. Règle : journal/2026-11-14_monde-dechet.md.
"""

from __future__ import annotations

import argparse

import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import IMMOBILE, MARCHEUR, REACTIF, Monde, Vie

TYPES = {"immobile": IMMOBILE, "marcheur": MARCHEUR, "réactif": REACTIF}


def started(genotypes, monde, rng) -> Vie:
    """Population sans mutation dont l'ingestion est allumée au départ."""
    vie = Vie(genotypes, monde, rng, mutation_rate=0.0)
    vie.brain[:] = (1, 0, 0)
    return vie


def monoculture(genotype, monde, steps, seed):
    vie = started(np.stack([genotype] * 300), monde, np.random.default_rng(seed))
    for _ in range(steps // 2):
        vie.step()
    vie.stats()
    sizes, waste = [], []
    for _ in range(steps // 2):
        vie.step()
        sizes.append(len(vie))
        waste.append(vie.waste.mean())
        if not len(vie):
            break
    return np.mean(sizes), np.mean(waste), vie.stats()


def competition(monde, steps, replicates, seed):
    shares = np.zeros((replicates, len(TYPES)))
    for r in range(replicates):
        genotypes = np.concatenate([np.stack([g] * 150) for g in TYPES.values()])
        vie = started(genotypes, monde, np.random.default_rng([seed, r]))
        for _ in range(steps):
            vie.step()
        kind = vie.lineage // 150
        shares[r] = np.bincount(kind, minlength=len(TYPES)) / max(len(vie), 1)
    return shares.mean(axis=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--steps", type=int, default=4000)
    parser.add_argument("--rep", type=int, default=6)
    parser.add_argument("--seed", type=int, default=0)
    for field, kind in Monde.__annotations__.items():
        if field not in ("height", "width", "neutral"):
            parser.add_argument(f"--{field}", type=eval(kind), default=getattr(Monde, field))
    args = parser.parse_args()
    params = {k: v for k, v in vars(args).items() if k not in ("steps", "rep", "seed")}
    espace = Monde(**params)
    print({k: v for k, v in params.items()})
    for name, monde in (("espace", espace), ("mélangé", espace.melange())):
        print(f"\n{name}")
        print(f"{'':10}{'effectif':>9}{'naiss./pas':>11}{'servies':>9}{'empois.':>9}{'déchet/case':>12}")
        for label, genotype in TYPES.items():
            n, waste, s = monoculture(genotype, monde, args.steps, args.seed)
            print(
                f"{label:10}{n:9.0f}{s['naissances']:11.2f}{100 * s['servies']:8.0f}%"
                f"{100 * s['empoisonnees']:8.0f}%{waste * monde.cells / espace.cells:12.2f}"
            )
        shares = competition(monde, args.steps, args.rep, args.seed)
        print("mélange des trois, parts finales : " + ", ".join(
            f"{label} {100 * x:.0f} %" for label, x in zip(TYPES, shares, strict=True)
        ))
    rng = np.random.default_rng([args.seed, 77])
    sizes = []
    for monde in (espace, espace.melange()):
        vie = Vie(ARCH.random(rng, 300, 3), monde, rng)
        trace = []
        for t in range(500):
            vie.step()
            if (t + 1) % 100 == 0:
                trace.append(len(vie))
        sizes.append(trace)
    print(f"\ngénotypes uniformes, effectif tous les 100 pas : espace {sizes[0]}, mélangé {sizes[1]}")


if __name__ == "__main__":
    main()
