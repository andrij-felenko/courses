"""
env_scanner.py — Сканування середовища та кодової бази на чистоту конфігурації.
Перевіряє 12-Factor змінні, повноту .env.example та детектує витік локальних абсолютних шляхів.
"""

from dataclasses import dataclass, field
from pathlib import Path
import os
import re


@dataclass
class ScanViolation:
    """Опис порушення гігієни середовища або витоку локальних шляхів."""

    file_path: str
    line_number: int
    violation_type: str
    message: str
    snippet: str


@dataclass
class ScanResult:
    """Підсумок перевірки середовища та кодової бази."""

    is_valid: bool
    missing_env_vars: list[str] = field(default_factory=list)
    violations: list[ScanViolation] = field(default_factory=list)
    scanned_files_count: int = 0


class EnvironmentScanner:
    """
    Аналізатор конфігураційних шаблонів і кодової бази на чистоту передачі.

    Перевіряє:
    1. Наявність усіх необхідних змінних із .env.example у поточному середовищі.
    2. Відсутність зашитих абсолютних локальних шляхів розробника (/home/..., C:\\Users\\...).
    3. Відсутність прихованих локальних артефактів перед передачею системи.
    """

    # Регулярні вирази для детекції витоку локальних шляхів попереднього розробника
    PATH_PATTERNS: list[tuple[str, re.Pattern]] = [
        (
            "hardcoded_unix_user_path",
            re.compile(r"""(?:/home/|/Users/)[a-zA-Z0-9._\-]+(?:/[^\s"'`<>]+)*"""),
        ),
        (
            "hardcoded_windows_user_path",
            re.compile(
                r"""[A-Za-z]:\\(?:Users|Documents and Settings)\\[a-zA-Z0-9._\-]+(?:\\[^\s"'`<>]+)*""",
                re.IGNORECASE,
            ),
        ),
        (
            "hardcoded_dev_workspace_path",
            re.compile(
                r"""[A-Za-z]:\\(?:develop|workspace|projects)\\[a-zA-Z0-9._\-]+""",
                re.IGNORECASE,
            ),
        ),
    ]

    DEFAULT_IGNORED_DIRS: set[str] = {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "dist",
        "build",
    }

    TEXT_EXTENSIONS: set[str] = {
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".env",
        ".example",
        ".sh",
        ".bash",
        ".dockerfile",
        ".sql",
        ".md",
        ".txt",
    }

    def check_env_template(
        self, example_file: Path, actual_env: dict[str, str] | None = None
    ) -> list[str]:
        """
        Перевіряє, чи всі ключі з .env.example присутні у фактичному середовищі.
        Змінні без значень або відсутні у системі вважаються порушенням 12-Factor гігієни.
        """
        if actual_env is None:
            actual_env = dict(os.environ)

        if not example_file.is_file():
            return [f"Файл шаблону змінних {example_file.name} не знайдено в корені проєкту"]

        missing: list[str] = []
        with open(example_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Отримуємо назву змінної до першого знака '='
                key = line.split("=", 1)[0].strip()
                if not key:
                    continue

                if key not in actual_env or not actual_env[key].strip():
                    missing.append(key)

        return missing

    def scan_files_for_paths(
        self, root_dir: Path, ignored_dirs: set[str] | None = None
    ) -> tuple[list[ScanViolation], int]:
        """
        Рекурсивно сканує текстові файли проєкту на наявність локальних абсолютних шляхів.
        """
        if ignored_dirs is None:
            ignored_dirs = self.DEFAULT_IGNORED_DIRS

        violations: list[ScanViolation] = []
        scanned_count = 0

        for path in root_dir.rglob("*"):
            if path.is_dir():
                continue

            if any(part in ignored_dirs for part in path.parts):
                continue

            if path.suffix.lower() not in self.TEXT_EXTENSIONS and not path.name.startswith(".env"):
                continue

            scanned_count += 1
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                # Пропускаємо власні рядки визначення регулярних виразів
                if path.name == "env_scanner.py" and ("re.compile" in line or "PATH_PATTERNS" in line):
                    continue

                for vtype, pattern in self.PATH_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        rel_path = str(path.relative_to(root_dir))
                        violations.append(
                            ScanViolation(
                                file_path=rel_path,
                                line_number=line_no,
                                violation_type=vtype,
                                message=f"Зашитий локальний шлях: '{match.group(0)}'",
                                snippet=line.strip()[:120],
                            )
                        )
                        break

        return violations, scanned_count

    def scan(
        self,
        project_dir: Path,
        example_filename: str = ".env.example",
        actual_env: dict[str, str] | None = None,
    ) -> ScanResult:
        """
        Виконує повний аудит гігієни середовища: шаблон конфігурацій та пошук зашитих шляхів.
        """
        example_file = project_dir / example_filename
        missing_vars = self.check_env_template(example_file, actual_env)
        violations, scanned_count = self.scan_files_for_paths(project_dir)

        is_valid = (len(missing_vars) == 0) and (len(violations) == 0)

        return ScanResult(
            is_valid=is_valid,
            missing_env_vars=missing_vars,
            violations=violations,
            scanned_files_count=scanned_count,
        )
