#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Render portable templates into a NEW preview folder; never install them."""
import argparse
import getpass
import socket
from pathlib import Path


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    root = Path(__file__).resolve().parents[1]
    home = Path.home().resolve()
    output = args.output.expanduser().resolve()
    unsafe = [home / part for part in [".config", ".local", ".var", ".ssh", ".gnupg"]]
    if output == home or output == root or any(output == p or output.is_relative_to(p) for p in unsafe):
        raise SystemExit("Usa una carpeta de vista previa, no una configuración activa")
    if output.exists():
        raise SystemExit("La carpeta de salida ya existe; no se sobrescribirá")
    plan = []
    for source in sorted((root / "home").rglob("*")):
        if not source.is_file():
            continue
        if source.is_symlink():
            raise SystemExit("No se procesan enlaces simbólicos")
        text = source.read_text().replace("@HOME@", str(home)).replace("@USER@", getpass.getuser()).replace("@HOST@", socket.gethostname())
        plan.append((source.relative_to(root / "home"), text))
    output.mkdir(parents=True)
    for relative, text in plan:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    print(f"Preparados {len(plan)} archivos en {output}. No se instaló ni recargó nada.")


if __name__ == "__main__":
    main()
