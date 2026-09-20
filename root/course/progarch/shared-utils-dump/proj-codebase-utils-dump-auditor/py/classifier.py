"""
classifier.py
Модуль аналізу та класифікації аномалій у спільних утилітах.
Класифікує утиліти за принципами CRP та REP на основі метрик Ca та наявності доменних типів.
"""

from typing import List, Set, Dict
from models import (
    FunctionSignature,
    CallReference,
    Finding,
    AuditReport,
    UtilityCategory,
)


class UtilityClassifier:
    """Конвеєр аналізу архітектурних правил та класифікації функцій утиліт."""

    def __init__(self, domain_types: List[str]):
        self.domain_types = [dt.strip() for dt in domain_types if dt.strip()]

    def _detect_domain_leaks(self, signature: FunctionSignature) -> List[str]:
        """Виявляє наявність доменних типів у параметрах або поверненій аннотації функції."""
        leaks = []
        all_annotations = list(signature.type_annotations.values())
        if signature.return_annotation:
            all_annotations.append(signature.return_annotation)

        for ann in all_annotations:
            for dt in self.domain_types:
                if dt in ann:
                    if dt not in leaks:
                        leaks.append(dt)
        return leaks

    def classify(
        self,
        functions: List[FunctionSignature],
        calls: List[CallReference],
    ) -> AuditReport:
        """Проводить класифікацію функцій утиліт та будує зведений AuditReport."""
        calls_by_func: Dict[str, List[CallReference]] = {
            f.name: [] for f in functions
        }
        for call in calls:
            if call.function_name in calls_by_func:
                calls_by_func[call.function_name].append(call)

        findings: List[Finding] = []
        category_stats: Dict[str, int] = {cat.value: 0 for cat in UtilityCategory}

        for func in functions:
            func_calls = calls_by_func.get(func.name, [])
            unique_clients = sorted(list(set(c.consumer_module for c in func_calls)))
            ca_score = len(unique_clients)

            domain_leaks = self._detect_domain_leaks(func)

            if domain_leaks:
                category = UtilityCategory.DOMAIN_LEAK
                leaks_str = ", ".join(domain_leaks)
                recommendation = (
                    f"Витік бізнес-логіки: сигнатура містить доменні типи [{leaks_str}]. "
                    f"Перенесіть функцію в відповідний доменний модуль за принципом REP."
                )
            elif ca_score == 0:
                category = UtilityCategory.DEAD_CODE
                recommendation = (
                    "Мертвий код (Ca=0): функція не використовується в кодовій базі. "
                    "Видаліть її або задокументуйте як експортовану бібліотеку."
                )
            elif ca_score == 1:
                category = UtilityCategory.LOCAL_HELPER
                client_name = unique_clients[0]
                recommendation = (
                    f"Локальний хелпер (Ca=1): функція викликається лише в модулі '{client_name}'. "
                    f"Перенесіть (інлайніть) її безпосередньо в модуль споживача за принципом CRP."
                )
            else:
                category = UtilityCategory.SHARED_LIBRARY
                recommendation = (
                    f"Спільна бібліотека (Ca={ca_score}): легітимна утиліта, що активно "
                    f"виристовується багатьма модулями без витоків доменних типів."
                )

            category_stats[category.value] += 1

            finding = Finding(
                function_name=func.name,
                file_path=func.file_path,
                line_number=func.line_number,
                category=category,
                ca_score=ca_score,
                clients=unique_clients,
                recommendation=recommendation,
            )
            findings.append(finding)

        violations_count = (
            category_stats[UtilityCategory.DEAD_CODE.value]
            + category_stats[UtilityCategory.LOCAL_HELPER.value]
            + category_stats[UtilityCategory.DOMAIN_LEAK.value]
        )
        passed = violations_count == 0

        return AuditReport(
            total_utilities=len(functions),
            findings=findings,
            category_stats=category_stats,
            passed=passed,
        )
