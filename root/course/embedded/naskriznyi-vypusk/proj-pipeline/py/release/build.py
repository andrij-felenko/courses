# -*- coding: utf-8 -*-
"""Ворота 2 і 3 — герметична матрична крос-збірка й бюджет Flash."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .config import HARDWARE_TARGETS, fail, log

STAGE = "G2-BUILD"


def _hermetic_env(tag_info: dict) -> dict:
    env = os.environ.copy()
    # Три змінні, без яких два прогони дають два різні бінарники.
    env["SOURCE_DATE_EPOCH"] = str(tag_info["epoch"])
    env["LC_ALL"] = "C"
    env["TZ"] = "UTC"
    # ccache з різних гілок ламає відтворюваність тихіше за все інше.
    env.pop("CCACHE_DIR", None)
    return env


def _run(cmd: list[str], env: dict, what: str) -> None:
    log(STAGE, " ".join(cmd))
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        fail(STAGE, f"{what}: код {res.returncode}")


def _check_flash_budget(hw_name: str, raw_bin: Path, limit: int) -> int:
    """Ворота 3. Перевищення хоч на байт — термінальний стан."""
    size = raw_bin.stat().st_size
    if size == 0:
        fail(STAGE, f"{raw_bin.name} порожній — лінкування дало нульовий образ")
    headroom = limit - size
    log(STAGE, f"{raw_bin.name}: {size} Б із {limit} Б "
               f"(запас {headroom} Б, {100.0 * size / limit:.1f}% слота)")
    if size > limit:
        fail(STAGE, f"пробито бюджет Flash для {hw_name}: "
                    f"{size} > {limit} Б, зайве {-headroom} Б")
    if headroom < limit // 20:
        # Не провал, але наступний патч уже може не влізти.
        log(STAGE, f"УВАГА: у слоті {hw_name} лишилося менше 5% місця")
    return size


def step_2_build_matrix(tag_info: dict, work_dir: Path) -> dict:
    """Збирає кожну ревізію своїм пресетом і складає артефакти у work_dir."""
    log(STAGE, "запуск герметичної матричної збірки…")
    env = _hermetic_env(tag_info)
    repo = Path.cwd()
    built: dict[str, dict] = {}

    for hw_name, target in HARDWARE_TARGETS.items():
        log(STAGE, f"ціль {hw_name} ({target['mcu']}), пресет {target['preset']}")
        build_dir = repo / target["build_dir"]

        # Кеш минулого прогону пам'ятає старі -D і старий тулчейн; для релізу
        # дерево збірки завжди нове.
        if build_dir.exists():
            shutil.rmtree(build_dir)

        _run([
            "cmake", "--preset", target["preset"],
            f"-DFW_VERSION_MAJOR={tag_info['major']}",
            f"-DFW_VERSION_MINOR={tag_info['minor']}",
            f"-DFW_VERSION_PATCH={tag_info['patch']}",
            f"-DFW_COMMIT_HASH=0x{tag_info['commit'][:8]}",
            f"-DFW_HW_MASK={target['hw_mask']}",
        ], env, f"конфігурація CMake для {hw_name}")

        _run(["cmake", "--build", "--preset", target["preset"]],
             env, f"компіляція прошивки для {hw_name}")

        raw_bin = build_dir / f"app-{hw_name}.raw.bin"
        elf_file = build_dir / f"app-{hw_name}.elf"
        for artefact in (raw_bin, elf_file):
            if not artefact.exists():
                fail(STAGE, f"збірка {hw_name} не дала {artefact.name}: "
                            "перевір ім'я цілі в CMakeLists")

        size = _check_flash_budget(hw_name, raw_bin, target["flash_limit"])

        # Артефакти копіюємо до себе: далі конвеєр не залежить від дерева
        # збірки, і його можна знести, не зачепивши реліз.
        staged_bin = work_dir / raw_bin.name
        staged_elf = work_dir / elf_file.name
        shutil.copy2(raw_bin, staged_bin)
        shutil.copy2(elf_file, staged_elf)

        built[hw_name] = {
            "raw_bin": staged_bin,
            "elf": staged_elf,
            "size": size,
            "target": target,
        }

    log(STAGE, f"зібрано цілей: {len(built)}")
    return built
