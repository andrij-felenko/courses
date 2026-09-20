"""
models.py
Модуль моделей даних статичного аналізатора спільних утиліт.
Містить енумератори, незмінні метадані функцій, структури точок викликів,
знахідок аномалій та підсумкового звіту аудиту.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class UtilityCategory(str, Enum):
    """Категорії класифікації функцій утиліт відповідно до принципів CRP та REP."""
    DEAD_CODE = "DEAD_CODE"          # Мертвий код (Ca = 0)
    LOCAL_HELPER = "LOCAL_HELPER"    # Локальний хелпер (Ca = 1, під інлайнінг)
    DOMAIN_LEAK = "DOMAIN_LEAK"      # Витік бізнес-логіки (доменні типи в сигнатурі)
    SHARED_LIBRARY = "SHARED_LIBRARY"  # Легітимна спільна бібліотека (Ca >= 2)


@dataclass(frozen=True)
class FunctionSignature:
    """Незмінна структура даних із метаданими функції утиліти."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    type_annotations: Dict[str, str] = field(default_factory=dict)
    return_annotation: Optional[str] = None


@dataclass
class CallReference:
    """Структура даних виявленого звернення до функції утиліти."""
    consumer_module: str
    line_number: int
    import_style: str
    function_name: str


@dataclass
class Finding:
    """Модель результату аудиту окремої функції утиліти."""
    function_name: str
    file_path: str
    line_number: int
    category: UtilityCategory
    ca_score: int
    clients: List[str]
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        """Серіалізує об'єкт Finding у словник."""
        return {
            "function_name": self.function_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "category": self.category.value,
            "ca_score": self.ca_score,
            "clients": self.clients,
            "recommendation": self.recommendation,
        }


@dataclass
class AuditReport:
    """Зведена структура результатів статичного аналізу кодової бази."""
    total_utilities: int
    findings: List[Finding]
    category_stats: Dict[str, int]
    passed: bool

    def to_dict(self) -> Dict[str, Any]:
        """Серіалізує об'єкт AuditReport у словник для JSON-звіту."""
        return {
            "total_utilities": self.total_utilities,
            "passed": self.passed,
            "category_stats": self.category_stats,
            "findings": [f.to_dict() for f in self.findings],
        }
