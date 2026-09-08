"""
Доменні моделі та структури даних митного контуру перевірок.
Визначає уніфіковані класи результатів аудиту, правил архітектури та ліцензійних політик.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Рівень критичності зафіксованого порушення."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Violation:
    """Одиничне зафіксоване порушення інженерних вимог у кодовій базі."""
    rule_name: str
    file_path: str
    line_number: int
    message: str
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict[str, Any]:
        """Серіалізує порушення у словник для звітності."""
        return {
            "rule": self.rule_name,
            "file": self.file_path,
            "line": self.line_number,
            "message": self.message,
            "severity": self.severity.value,
        }


@dataclass
class CheckResult:
    """Узагальнений результат роботи окремого інспектора митного контуру."""
    check_name: str
    passed: bool
    violations: list[Violation] = field(default_factory=list)
    summary: str = ""

    @property
    def error_count(self) -> int:
        """Кількість критичних помилок, що блокують злиття."""
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Кількість застережень, що потребують уваги, але не блокують збірку."""
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)


@dataclass
class LayerRule:
    """Правило ізоляції архітектурного шару: заборонені напрямки імпорту."""
    source_layer: str
    forbidden_targets: list[str]


@dataclass
class LicensePolicy:
    """Політика допустимості ліцензій сторонніх бібліотек замовника."""
    allowed_licenses: set[str] = field(default_factory=lambda: {
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Python-2.0", "PSF-2.0"
    })
    forbidden_licenses: set[str] = field(default_factory=lambda: {
        "GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL", "LGPL-2.1", "LGPL-3.0", "EUPL-1.2"
    })
