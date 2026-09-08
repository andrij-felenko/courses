"""
Модуль перевірки критеріїв Quality Gate та розрахунку Mutation Score.
"""

from dataclasses import dataclass, field
from typing import Optional
from mutmut_runner import MutantRecord, MutantStatus


@dataclass
class QualityGateConfig:
    """Конфігураційні пороги для приймання результатів мутаційного тестування."""
    min_score_percent: float = 80.0       # Мінімально допустимий Mutation Score (у %)
    fail_on_survived: bool = True         # Чи блокувати збірку за наявності хоча б одного мутанта, що вижив
    fail_on_timeout: bool = False        # Чи вважати таймаути блокуючими помилками


@dataclass
class QualityGateResult:
    """Підсумковий вердикт мутаційного контролю приймання."""
    passed: bool
    score: float
    threshold: float
    total_mutants: int
    killed: int
    survived: int
    timeout: int
    suspicious: int
    reasons: list[str] = field(default_factory=list)


class MutationQualityGate:
    """
    Оцінювач мутаційного покриття проти нормативних критеріїв Definition of Done.
    """

    def evaluate(
        self,
        mutants: list[MutantRecord],
        config: Optional[QualityGateConfig] = None
    ) -> QualityGateResult:
        """
        Розраховує Mutation Score та перевіряє дотримання інженерних обмежень.
        """
        if config is None:
            config = QualityGateConfig()

        total = len(mutants)
        killed = sum(1 for m in mutants if m.status == MutantStatus.KILLED)
        survived = sum(1 for m in mutants if m.status == MutantStatus.SURVIVED)
        timeout = sum(1 for m in mutants if m.status == MutantStatus.TIMEOUT)
        suspicious = sum(1 for m in mutants if m.status == MutantStatus.SUSPICIOUS)

        if total > 0:
            score = (killed / total) * 100.0
        else:
            # Якщо цільових мутацій не згенеровано, вважаємо гейт пройденим
            score = 100.0

        reasons: list[str] = []

        # Критерій 1: Загальний відсоток знищених мутантів
        if score < config.min_score_percent:
            reasons.append(
                f"Mutation Score {score:.1f}% є нижчим за обов'язковий поріг {config.min_score_percent:.1f}%"
            )

        # Критерій 2: Наявність мутантів, що вижили в модифікованому коді
        if config.fail_on_survived and survived > 0:
            reasons.append(
                f"Виявлено {survived} мутантів, що вижили, у зміненій бізнес-логіці підрядника"
            )

        # Критерій 3: Наявність аномальних таймаутів
        if config.fail_on_timeout and timeout > 0:
            reasons.append(
                f"Виявлено {timeout} мутацій, що призвели до зависання тестового процесу"
            )

        passed = (len(reasons) == 0)

        return QualityGateResult(
            passed=passed,
            score=round(score, 2),
            threshold=config.min_score_percent,
            total_mutants=total,
            killed=killed,
            survived=survived,
            timeout=timeout,
            suspicious=suspicious,
            reasons=reasons
        )
