"""
Модуль перевірки ліцензійної чистоти сторонніх залежностей у lock-файлах.
Запобігає потраплянню вірусних копілефт-ліцензій (GPL, AGPL) у комерційні проєкти замовника.
"""

import re
from pathlib import Path
from typing import Optional

from models import CheckResult, LicensePolicy, Severity, Violation


class LockfileLicenseScanner:
    """
    Сканер маніфестів блокування залежностей (poetry.lock, requirements.txt).
    """

    KNOWN_LICENSES: dict[str, str] = {
        "requests": "Apache-2.0",
        "urllib3": "MIT",
        "certifi": "MPL-2.0",
        "charset-normalizer": "MIT",
        "idna": "BSD-3-Clause",
        "pytest": "MIT",
        "iniconfig": "MIT",
        "packaging": "Apache-2.0",
        "pluggy": "MIT",
        "pydantic": "MIT",
        "fastapi": "MIT",
        "starlette": "BSD-3-Clause",
        "sqlalchemy": "MIT",
        "alembic": "MIT",
        "pika": "BSD-3-Clause",
        "celery": "BSD-3-Clause",
        "redis": "MIT",
        "pyyaml": "MIT",
        "click": "BSD-3-Clause",
        "httpx": "BSD-3-Clause",
        "mutmut": "BSD-3-Clause",
        "gpl-unapproved-driver": "GPL-3.0",
        "agpl-telemetry-sdk": "AGPL-3.0",
    }

    def __init__(self, policy: Optional[LicensePolicy] = None, lockfile_path: Optional[str] = None):
        self.policy = policy or LicensePolicy()
        self.lockfile_path = Path(lockfile_path) if lockfile_path else None

    def parse_poetry_lock(self, content: str) -> list[dict[str, str]]:
        """
        Парсить вміст poetry.lock (формат TOML) без сторонніх бібліотек.
        """
        packages: list[dict[str, str]] = []
        current_pkg: Optional[dict[str, str]] = None

        for line in content.splitlines():
            line = line.strip()
            if line == "[[package]]":
                if current_pkg and "name" in current_pkg:
                    packages.append(current_pkg)
                current_pkg = {}
                continue

            if current_pkg is not None:
                if line.startswith("name = "):
                    m = re.match(r'name\s*=\s*"([^"]+)"', line)
                    if m:
                        current_pkg["name"] = m.group(1).lower()
                elif line.startswith("version = "):
                    m = re.match(r'version\s*=\s*"([^"]+)"', line)
                    if m:
                        current_pkg["version"] = m.group(1)
                elif line.startswith("license = "):
                    m = re.match(r'license\s*=\s*"([^"]+)"', line)
                    if m:
                        current_pkg["license"] = m.group(1)

        if current_pkg and "name" in current_pkg:
            packages.append(current_pkg)
        return packages

    def parse_requirements_txt(self, content: str) -> list[dict[str, str]]:
        """
        Парсить requirements.txt і виділяє перелік назв пакетів та їх версій.
        """
        packages: list[dict[str, str]] = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            m = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:[=><~]+([0-9a-zA-Z\.\-]+))?", line)
            if m:
                name = m.group(1).lower()
                version = m.group(2) or "unknown"
                packages.append({"name": name, "version": version})
        return packages

    def resolve_license(self, package_name: str, explicit_license: Optional[str] = None) -> str:
        """Визначає ліцензію пакета за метаданими або вбудованою базою знань."""
        if explicit_license:
            return explicit_license
        return self.KNOWN_LICENSES.get(package_name.lower(), "Unknown")

    def check_packages(self, packages: list[dict[str, str]], source_file: str) -> list[Violation]:
        """Зіставляє перелік знайдених бібліотек із затвердженими ліцензійними правилами."""
        violations: list[Violation] = []

        for pkg in packages:
            name = pkg.get("name", "unknown")
            version = pkg.get("version", "unknown")
            lic = self.resolve_license(name, pkg.get("license"))

            if any(forbidden.lower() in lic.lower() for forbidden in self.policy.forbidden_licenses):
                violations.append(
                    Violation(
                        rule_name="ForbiddenLicenseViolation",
                        file_path=source_file,
                        line_number=1,
                        message=(
                            f"Виявлено сторонній пакет '{name}' версії '{version}' із забороненою "
                            f"копілефт-ліцензією '{lic}'. Злиття заборонено через юридичні ризики."
                        ),
                        severity=Severity.ERROR
                    )
                )
            elif lic == "Unknown":
                violations.append(
                    Violation(
                        rule_name="UnknownLicenseWarning",
                        file_path=source_file,
                        line_number=1,
                        message=(
                            f"Пакет '{name}' версії '{version}' не має верифікованої ліцензії в базі. "
                            f"Потрібна ручна перевірка юристом або додавання у білий список."
                        ),
                        severity=Severity.WARNING
                    )
                )
            elif not any(allowed.lower() in lic.lower() for allowed in self.policy.allowed_licenses):
                violations.append(
                    Violation(
                        rule_name="UnapprovedLicenseWarning",
                        file_path=source_file,
                        line_number=1,
                        message=(
                            f"Ліцензія '{lic}' пакета '{name}' відсутня у списку автоматично дозволених."
                        ),
                        severity=Severity.WARNING
                    )
                )

        return violations

    def run(self, raw_content: Optional[str] = None, filename: Optional[str] = None) -> CheckResult:
        """Запускає аудит маніфесту залежностей."""
        file_to_read = self.lockfile_path
        source_name = filename or (str(file_to_read) if file_to_read else "poetry.lock")

        if raw_content is None and file_to_read and file_to_read.exists():
            with open(file_to_read, "r", encoding="utf-8") as f:
                content = f.read()
        elif raw_content is not None:
            content = raw_content
        else:
            return CheckResult(
                check_name="DependencyLicenseCheck",
                passed=True,
                violations=[],
                summary="Lock-файл не надано, перевірка залежностей пропущена."
            )

        if source_name.endswith(".lock"):
            packages = self.parse_poetry_lock(content)
        else:
            packages = self.parse_requirements_txt(content)

        violations = self.check_packages(packages, source_name)
        passed = all(v.severity != Severity.ERROR for v in violations)

        summary = (
            f"Проінспектовано пакетів: {len(packages)}. "
            f"Помилок: {sum(1 for v in violations if v.severity == Severity.ERROR)}, "
            f"Попереджень: {sum(1 for v in violations if v.severity == Severity.WARNING)}."
        )
        return CheckResult(
            check_name="DependencyLicenseCheck",
            passed=passed,
            violations=violations,
            summary=summary
        )
