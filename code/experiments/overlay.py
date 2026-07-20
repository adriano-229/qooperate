"""Superpone 2 o más imágenes PNG (pensado para las figuras transparentes
generadas por figures.py). El usuario es responsable de elegir imágenes
compatibles (misma escala/dominio: ej. todas de cooperación, o todas de
Gini, sobre el mismo rango de rondas).

Uso:
    python experiments/overlay.py <salida.png> <img1.png> <img2.png> [...]
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def overlay(paths: list[Path], out_path: Path) -> None:
    images = [Image.open(p).convert("RGBA") for p in paths]
    base = images[0]
    for img in images[1:]:
        if img.size != base.size:
            img = img.resize(base.size)
        base = Image.alpha_composite(base, img)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(out_path)
    print(f"Guardada: {out_path}")


def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    out_path = Path(sys.argv[1])
    paths = [Path(p) for p in sys.argv[2:]]
    overlay(paths, out_path)


if __name__ == "__main__":
    main()
