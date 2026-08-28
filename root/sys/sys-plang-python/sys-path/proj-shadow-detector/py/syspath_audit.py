#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""syspath_audit.py — інструмент діагностики безпеки sys.path та затінення модулів."""

from __future__ import annotations

import os
import sys
import stat
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class PathIssue:
    path: str
    severity: str  # "CRITICAL", "WARNING", "INFO"
    message: str


@dataclass
class ShadowConflict:
    module_name: str
    shadowing_path: Path
    shadowed_path: Path
    conflict_type: str  # "STDLIB_SHADOW", "SITE_SHADOW"


@dataclass
class AuditReport:
    path_issues: list[PathIssue] = field(default_factory=list)
    conflicts: list[ShadowConflict] = field(default_factory=list)
    scanned_paths: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.path_issues and not self.conflicts


class SysPathAuditor:
    def __init__(self, target_paths: list[str] | None = None) -> None:
        self.paths = target_paths if target_paths is not None else list(sys.path)
        # Отримання офіційного множинного індексу модулів стандартної бібліотеки
        if hasattr(sys, "stdlib_module_names"):
            self.stdlib_names = sys.stdlib_module_names
        else:
            # Fallback для версій Python < 3.10
            import distutils.sysconfig
            self.stdlib_names = set(sys.builtin_module_names)

    def audit_path_structure(self) -> list[PathIssue]:
        issues: list[PathIssue] = []
        seen_realpaths: set[str] = set()

        for idx, raw_path in enumerate(self.paths):
            # 1. Перевірка на небезпечний порожній рядок або відносний шлях
            if raw_path == "" or raw_path == ".":
                issues.append(PathIssue(
                    path=raw_path,
                    severity="CRITICAL",
                    message=f"Позиція [{idx}]: Порожній або відносний шлях відкриває вразливість локального затінення (CWD injection)."
                ))
                continue

            p = Path(raw_path)
            if not p.is_absolute():
                issues.append(PathIssue(
                    path=raw_path,
                    severity="WARNING",
                    message=f"Позиція [{idx}]: Відносний шлях '{raw_path}' залежить від поточного каталогу виклику процесу."
                ))

            if not p.exists():
                issues.append(PathIssue(
                    path=raw_path,
                    severity="INFO",
                    message=f"Позиція [{idx}]: Каталог не існує на диску."
                ))
                continue

            # 2. Перевірка дублікатів шляхів через розіменування symlink
            try:
                resolved = str(p.resolve())
                if resolved in seen_realpaths:
                    issues.append(PathIssue(
                        path=raw_path,
                        severity="WARNING",
                        message=f"Позиція [{idx}]: Дублікат шляху (канонічний шлях: '{resolved}')."
                    ))
                seen_realpaths.add(resolved)
            except OSError as err:
                issues.append(PathIssue(path=raw_path, severity="WARNING", message=f"Помилка доступу: {err}"))
                continue

            # 3. Перевірка небезпечних прав доступу на запис у POSIX системах
            if os.name == "posix":
                try:
                    st = p.stat()
                    if bool(st.st_mode & stat.S_IWOTH):
                        issues.append(PathIssue(
                            path=raw_path,
                            severity="CRITICAL",
                            message=f"Позиція [{idx}]: Каталог доступний для запису всім користувачам (World-writable)."
                        ))
                except OSError:
                    pass

        return issues

    def _discover_modules_in_dir(self, directory: Path) -> Iterator[tuple[str, Path]]:
        """Сканує каталог на наявність кореневих модулів та пакетів."""
        valid_extensions = {".py", ".pyc", ".so", ".pyd"}
        try:
            for entry in directory.iterdir():
                if entry.is_file():
                    ext = entry.suffix.lower()
                    if ext in valid_extensions:
                        # Відкидаємо суфікси компіляції на зразок .cpython-312-x86_64-linux-gnu
                        stem = entry.name.split(".")[0]
                        if stem != "__init__":
                            yield stem, entry
                elif entry.is_dir():
                    # Каталог є пакетом, якщо містить __init__.py або є namespace-пакетом
                    if (entry / "__init__.py").is_file():
                        yield entry.name, entry
        except (PermissionError, OSError):
            return

    def audit_shadowing(self) -> list[ShadowConflict]:
        conflicts: list[ShadowConflict] = []
        # Словник першого знайденого екземпляра кожного імені модуля: name -> (index, path)
        first_seen: dict[str, tuple[int, Path]] = {}

        for idx, raw_path in enumerate(self.paths):
            if not raw_path:
                raw_path = "."
            p = Path(raw_path)
            if not p.is_dir():
                continue

            for mod_name, file_path in self._discover_modules_in_dir(p):
                # 1. Перевірка затінення стандартної бібліотеки користувацькими каталогами
                # Якщо каталог скрипту містить файл зі списку stdlib (наприклад, math.py)
                is_stdlib = mod_name in self.stdlib_names
                is_user_dir = "site-packages" not in str(p) and "lib/python" not in str(p)

                if is_stdlib and is_user_dir:
                    conflicts.append(ShadowConflict(
                        module_name=mod_name,
                        shadowing_path=file_path,
                        shadowed_path=Path(f"<Standard Library Module: {mod_name}>"),
                        conflict_type="STDLIB_SHADOW"
                    ))

                # 2. Перевірка колізій між елементами sys.path різного пріоритету
                if mod_name in first_seen:
                    prev_idx, prev_path = first_seen[mod_name]
                    # Фіксуємо конфлікт, якщо модуль знайдено в двох різних фізичних місцях
                    if prev_path.resolve() != file_path.resolve():
                        conflicts.append(ShadowConflict(
                            module_name=mod_name,
                            shadowing_path=prev_path,
                            shadowed_path=file_path,
                            conflict_type="SITE_SHADOW"
                        ))
                else:
                    first_seen[mod_name] = (idx, file_path)

        return conflicts

    def run_full_audit(self) -> AuditReport:
        report = AuditReport(scanned_paths=self.paths)
        report.path_issues = self.audit_path_structure()
        report.conflicts = self.audit_shadowing()
        return report


def print_cli_report(report: AuditReport) -> None:
    print("=" * 70)
    print("                 ЗВІТ АУДИТУ БЕЗПЕКИ SYS.PATH")
    print("=" * 70)

    print(f"\n[+] Проскановано {len(report.scanned_paths)} записів у sys.path.")

    if report.path_issues:
        print(f"\n[!] Виявлено структурні дефекти шляхів ({len(report.path_issues)}):")
        for issue in report.path_issues:
            color_mark = "CRITICAL: " if issue.severity == "CRITICAL" else "WARNING:  "
            print(f"  • [{color_mark}] {issue.message}")
            print(f"    Шлях: '{issue.path}'")
    else:
        print("\n[✓] Структурних проблем у записах sys.path не знайдено.")

    if report.conflicts:
        print(f"\n[!] Виявлено колізії імен та затінення модулів ({len(report.conflicts)}):")
        for conf in report.conflicts:
            if conf.conflict_type == "STDLIB_SHADOW":
                print(f"  • [STDLIB SHADOW] Модуль '{conf.module_name}' затіняє стандартну бібліотеку!")
                print(f"    Файл затінення: {conf.shadowing_path}")
            else:
                print(f"  • [PATH COLLISION] Модуль '{conf.module_name}' продубльовано на різних рівнях:")
                print(f"    Пріоритетний:  {conf.shadowing_path}")
                print(f"    Затінений:    {conf.shadowed_path}")
    else:
        print("\n[✓] Небезпечних затінень модулів не виявлено.")

    print("\n" + "=" * 70)
    if report.is_clean:
        print("РЕЗУЛЬТАТ: СЕРЕДОВИЩЕ ЧИСТЕ. Затінень та вразливих шляхів немає.")
    else:
        print("РЕЗУЛЬТАТ: ВИЯВЛЕНО РИЗИКИ. Перевірте локальні файли та налаштування CWD.")
    print("=" * 70)


if __name__ == "__main__":
    auditor = SysPathAuditor()
    report = auditor.run_full_audit()
    print_cli_report(report)
    if not report.is_clean:
        sys.exit(1)
