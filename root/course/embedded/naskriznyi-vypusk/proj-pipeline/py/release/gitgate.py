# -*- coding: utf-8 -*-
"""Ворота 1 — джерело: чисте дерево, підписаний тег, SemVer, мітка часу."""
from __future__ import annotations

import re
import subprocess

from .config import AUTHORIZED_RELEASE_KEY_FINGERPRINTS, fail, log

STAGE = "G1-TAG"

_SEMVER_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
_FINGERPRINT_RE = re.compile(r"[0-9A-F]{40}")


def _git(*args: str, allow_fail: bool = False) -> subprocess.CompletedProcess:
    res = subprocess.run(["git", *args], capture_output=True, text=True)
    if res.returncode != 0 and not allow_fail:
        fail(STAGE, f"git {' '.join(args)} → код {res.returncode}\n{res.stderr.strip()}")
    return res


def _fingerprints(text: str) -> set[str]:
    """Витягує відбитки з виводу gpg.

    gpg друкує їх то суцільним рядком ('using EDDSA key 9E8B…'), то групами
    по чотири символи ('Primary key fingerprint: 9E8B 7A6C …'), тож пробіли
    з кожного рядка спершу викидаємо.
    """
    found: set[str] = set()
    for line in text.splitlines():
        found.update(_FINGERPRINT_RE.findall(line.replace(" ", "").upper()))
    return found


def step_1_validate_git_tag(tag_name: str) -> dict:
    """Повертає опис випуску або валить конвеєр до першого запуску компілятора."""
    log(STAGE, f"перевірка криптографічного тегу {tag_name}…")

    # 1. Робоче дерево. Забутий файл налагодження потрапив би в прошивку,
    #    а в маніфесті стояв би хеш чистого коміту — реліз збрехав би.
    dirty = _git("status", "--porcelain")
    if dirty.stdout.strip():
        fail(STAGE, "робоче дерево містить незафіксовані зміни:\n"
                    + dirty.stdout.strip())

    # 2. Тег мусить бути об'єктом-тегом, а не легковісним посиланням:
    #    підпису на легковісному тегу немає де лежати.
    kind = _git("cat-file", "-t", tag_name, allow_fail=True)
    if kind.returncode != 0:
        fail(STAGE, f"тегу {tag_name} немає в репозиторії "
                    "(неглибоке клонування? потрібен fetch-depth: 0)")
    if kind.stdout.strip() != "tag":
        fail(STAGE, f"{tag_name} — легковісний тег без підпису; "
                    "реліз позначають анотованим підписаним тегом")

    # 3. Підпис і його автор.
    verify = _git("tag", "-v", tag_name, allow_fail=True)
    if verify.returncode != 0:
        fail(STAGE, f"тег {tag_name} не має дійсного підпису GPG/SSH:\n"
                    + verify.stderr.strip())

    signers = _fingerprints(verify.stderr + verify.stdout)
    allowed = signers & AUTHORIZED_RELEASE_KEY_FINGERPRINTS
    if not allowed:
        fail(STAGE, "підпис дійсний, але ключ не в списку релізних відбитків; "
                    f"побачено: {', '.join(sorted(signers)) or '—'}")
    log(STAGE, f"підписав ключ {sorted(allowed)[0]}")

    # 4. Семантична версія.
    match = _SEMVER_RE.match(tag_name)
    if match is None:
        fail(STAGE, f"ім'я тегу '{tag_name}' не є vMAJOR.MINOR.PATCH")
    major, minor, patch = (int(part) for part in match.groups())
    if max(major, minor, patch) > 255:
        # У заголовку образу під кожне поле рівно один байт.
        fail(STAGE, f"версія {major}.{minor}.{patch} не влазить у заголовок: "
                    "кожне поле — один байт")

    # 5. Мітка часу коміту як SOURCE_DATE_EPOCH: інакше два раннери зберуть
    #    два різні бінарники з одного коду через __DATE__ у логах збірки.
    commit = _git("rev-list", "-n", "1", tag_name).stdout.strip()
    epoch_raw = _git("log", "-1", "--format=%ct", commit).stdout.strip()
    if not epoch_raw.isdigit():
        fail(STAGE, f"не вдалося прочитати час коміту {commit}")
    epoch = int(epoch_raw)

    log(STAGE, f"валідовано: {tag_name[1:]}, коміт {commit[:8]}, епоха {epoch}")
    return {
        "tag": tag_name,
        "version_str": tag_name[1:],
        "major": major,
        "minor": minor,
        "patch": patch,
        "commit": commit,
        "epoch": epoch,
    }
