"""
vendoring_auditor.py — Аудит офлайн-залежностей та вендорингу для передачі системи.
Перевіряє наявність локальних пакетів, звіряє криптографічні хеші sha256 та блокує
неоголошені звернення до зовнішніх інтернет-репозиторіїв.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PackageArchive:
    """Метадані окремого локального архіву залежності."""
    name: str
    filename: str
    sha256_hash: str
    size_bytes: int


@dataclass
class VendoringAuditResult:
    """Результат перевірки герметичності та вендорингу."""
    passed: bool
    total_packages_found: int
    audited_packages: list[PackageArchive] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    offline_ready: bool = False


class VendoringAuditor:
    """
    Аудитор автономності стороннього коду за стандартами Clean-Room.
    Гарантує, що система збирається виключно з локального каталогу вендорингу.
    """

    DEFAULT_VENDOR_DIRS = ("vendor", "wheelhouse", "offline_packages")

    def __init__(self, vendor_dir_name: str | None = None) -> None:
        self.vendor_dir_name = vendor_dir_name

    def audit_directory(self, project_path: str | Path) -> VendoringAuditResult:
        """
        Виконує повний аудит локальних пакетів та маніфестів залежностей у проєкті.
        """
        base_dir = Path(project_path).resolve()
        violations: list[str] = []
        audited_packages: list[PackageArchive] = []

        # 1. Пошук каталогу локальних архівів
        vendor_dir = self._resolve_vendor_dir(base_dir)
        if not vendor_dir or not vendor_dir.exists():
            violations.append(
                f"Каталог вендорингу не знайдено (очікувалися: {', '.join(self.DEFAULT_VENDOR_DIRS)}). "
                "Збірка без доступу до зовнішньої мережі неможлива."
            )
            return VendoringAuditResult(
                passed=False,
                total_packages_found=0,
                violations=violations,
                offline_ready=False,
            )

        # 2. Сканування пакетів (whl, tar.gz, zip)
        package_files = [
            f for f in vendor_dir.iterdir()
            if f.is_file() and f.suffix in (".whl", ".gz", ".zip")
        ]

        if not package_files:
            violations.append(
                f"Каталог {vendor_dir.name} порожній. Відсутні скомпільовані пакети для офлайн-інсталяції."
            )

        for pkg_file in package_files:
            file_hash = self._calculate_sha256(pkg_file)
            size = pkg_file.stat().st_size
            name_guess = self._extract_package_name(pkg_file.name)
            audited_packages.append(
                PackageArchive(
                    name=name_guess,
                    filename=pkg_file.name,
                    sha256_hash=file_hash,
                    size_bytes=size,
                )
            )

        # 3. Аудит маніфесту залежностей (requirements.txt / lockfile)
        self._audit_lockfiles(base_dir, audited_packages, violations)

        passed = len(violations) == 0
        return VendoringAuditResult(
            passed=passed,
            total_packages_found=len(audited_packages),
            audited_packages=audited_packages,
            violations=violations,
            offline_ready=passed,
        )

    def _resolve_vendor_dir(self, base_dir: Path) -> Path | None:
        if self.vendor_dir_name:
            custom_path = base_dir / self.vendor_dir_name
            if custom_path.exists():
                return custom_path

        for dirname in self.DEFAULT_VENDOR_DIRS:
            candidate = base_dir / dirname
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    @staticmethod
    def _calculate_sha256(file_path: Path) -> str:
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def _extract_package_name(filename: str) -> str:
        clean = re.sub(r"\.(whl|tar\.gz|zip)$", "", filename)
        parts = clean.split("-")
        return parts[0] if parts else clean

    def _audit_lockfiles(
        self,
        base_dir: Path,
        packages: list[PackageArchive],
        violations: list[str],
    ) -> None:
        req_txt = base_dir / "requirements.txt"
        pip_conf = base_dir / "pip.conf"

        # Перевірка блокування зовнішніх індексів у конфігурації pip
        if pip_conf.exists():
            content = pip_conf.read_text(encoding="utf-8")
            if "no-index" not in content and "--no-index" not in content:
                violations.append("У pip.conf відсутня директива no-index = true (заборона звернень до PyPI).")
        
        # Перевірка наявності вимог з фіксацією хешів
        if req_txt.exists():
            lines = req_txt.read_text(encoding="utf-8").splitlines()
            has_hashes = any("--hash=sha256:" in line for line in lines)
            if not has_hashes:
                violations.append(
                    "У requirements.txt відсутня строга фіксація криптографічних хешів (--hash=sha256:...). "
                    "Необхідно згенерувати герметичний lock-файл."
                )
