"""Choix du fondateur unique (une fois pour toutes), selon le critère du journal.

    python experiments/fondateur/fondateur.py    # écrit out/fondateur.npy et out/fondateur.txt

Protocole : journal/2026-11-15_fondateur-unique.md. Génotypes tirés au hasard (flux
[0, 7, 0]) ; on garde le premier dont 300 clones, sans mutation, dans le monde du régime
« directions » pendant 3 000 pas ne s'éteignent pas et ont un effectif moyen d'au moins
100 sur les 500 derniers pas.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from simsbn.monde import Corps, Monde, Vie

HERE = Path(__file__).parent
BOUND = 3
MONDE = Monde()  # paramètres figés dans journal/2026-11-14_monde-dechet.md
CORPS = Corps(("ingérer", "nord", "sud", "est", "ouest"), ticks=2)
STEPS, LAST, MINIMUM, POP = 3_000, 500, 100, 300


def effectif_moyen(candidate: np.ndarray, index: int) -> tuple[float, bool]:
    """Effectif moyen sur les derniers pas de 300 clones sans mutation, et extinction."""
    rng = np.random.default_rng([0, 7, 1, index])
    vie = Vie(np.repeat(candidate[None], POP, axis=0), MONDE, rng, 0.0, BOUND, CORPS)
    sizes = []
    for t in range(STEPS):
        vie.step()
        if not len(vie):
            return 0.0, True
        if t >= STEPS - LAST:
            sizes.append(len(vie))
    return float(np.mean(sizes)), False


def main():
    rng = np.random.default_rng([0, 7, 0])
    log = []
    for index in range(1, 1001):
        candidate = CORPS.arch.random(rng, 1, BOUND)[0]
        mean, extinct = effectif_moyen(candidate, index)
        log.append(f"candidat {index:4d} : {'éteint' if extinct else f'effectif {mean:6.1f}'}")
        print(log[-1])
        if not extinct and mean >= MINIMUM:
            break
    else:
        raise SystemExit("aucun candidat viable en 1000 essais")
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    np.save(out / "fondateur.npy", candidate)
    (out / "fondateur.txt").write_text("\n".join(log) + f"\nretenu : candidat {index}\n")
    print(f"retenu : candidat {index}\n{candidate[CORPS.arch.mask()]}")


if __name__ == "__main__":
    main()
