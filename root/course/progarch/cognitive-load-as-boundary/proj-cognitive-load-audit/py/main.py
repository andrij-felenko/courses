#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cognitive Load Audit & Service Boundary Evaluator v2.0
Комплексний інструмент оцінки когнітивного навантаження інженерних команд
та визначення доцільності розрозрізу або об'єднання мікросервісів.
"""

import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class SurveyScores:
    domain_q: List[float]       # Q1-Q4 (1.0 - 5.0)
    extraneous_q: List[float]   # Q5-Q8 (1.0 - 5.0)
    comm_q: List[float]         # Q9-Q12 (1.0 - 5.0)

@dataclass
class GitRepositoryTelemetry:
    team_name: str
    engineer_count: int
    active_services_count: int
    commit_history_sample: List[List[str]]  # Перелік модифікованих сервісів на кожен коміт
    pr_lead_time_avg_hours: float
    oncall_alerts_per_week: float

class CognitiveLoadAuditor:
    def __init__(self, survey: SurveyScores, telemetry: GitRepositoryTelemetry):
        self.survey = survey
        self.telemetry = telemetry

    def compute_survey_averages(self) -> Tuple[float, float, float]:
        domain_avg = sum(self.survey.domain_q) / len(self.survey.domain_q)
        extraneous_avg = sum(self.survey.extraneous_q) / len(self.survey.extraneous_q)
        comm_avg = sum(self.survey.comm_q) / len(self.survey.comm_q)
        return (round(domain_avg, 2), round(extraneous_avg, 2), round(comm_avg, 2))

    def compute_change_coupling_matrix(self) -> Dict[Tuple[str, str], float]:
        """Обчислює матрицю парного зачеплення змін між сервісами."""
        pair_counts: Dict[Tuple[str, str], int] = {}
        single_counts: Dict[str, int] = {}

        for commit in self.telemetry.commit_history_sample:
            unique_svcs = list(set(commit))
            for svc in unique_svcs:
                single_counts[svc] = single_counts.get(svc, 0) + 1
            
            for i in range(len(unique_svcs)):
                for j in range(i + 1, len(unique_svcs)):
                    pair = tuple(sorted([unique_svcs[i], unique_svcs[j]]))
                    pair_counts[pair] = pair_counts.get(pair, 0) + 1

        coupling_matrix: Dict[Tuple[str, str], float] = {}
        for (s1, s2), joint_count in pair_counts.items():
            base_count = min(single_counts[s1], single_counts[s2])
            ratio = joint_count / base_count if base_count > 0 else 0.0
            coupling_matrix[(s1, s2)] = round(ratio, 3)

        return coupling_matrix

    def evaluate(self) -> Dict[str, Any]:
        d_avg, e_avg, c_avg = self.compute_survey_averages()
        cli_base = (0.35 * d_avg) + (0.45 * e_avg) + (0.20 * c_avg)

        # Телеметричні штрафи
        penalties = 0.0
        penalty_reasons = []

        # 1. Штраф за співвідношення сервісів до людей
        svc_per_eng = self.telemetry.active_services_count / self.telemetry.engineer_count
        if svc_per_eng > 1.5:
            penalties += 0.5
            penalty_reasons.append(f"Занадто багато сервісів на людину: {svc_per_eng:.2f} (поріг 1.5)")

        # 2. Штраф за парне зачеплення змін
        coupling_matrix = self.compute_change_coupling_matrix()
        high_couplings = [pair for pair, ratio in coupling_matrix.items() if ratio > 0.35]
        if high_couplings:
            penalties += 0.4
            penalty_reasons.append(f"Високе зачеплення між сервісами: {high_couplings}")

        # 3. Штраф за навантаження on-call
        if self.telemetry.oncall_alerts_per_week > 5.0:
            penalties += 0.3
            penalty_reasons.append(f"Критичне навантаження on-call: {self.telemetry.oncall_alerts_per_week} алертів/тиждень")

        final_cli = min(5.0, cli_base + penalties)
        final_cli = round(final_cli, 2)

        # Визначення зони та інженерного вердикту
        if final_cli < 2.3:
            zone = "GREEN (Профіцит ємності)"
            verdict = "Залишити поточні межі. Команда працює автономно та володіє контекстом."
        elif final_cli <= 3.4:
            zone = "YELLOW (Оптимальне навантаження)"
            verdict = "Зрілий соціотехнічний баланс. Рекомендовано спостереження без радикальних реорганізацій."
        elif final_cli <= 4.2:
            zone = "ORANGE (Високий ризик вигорання)"
            if e_avg > 3.5:
                verdict = "ЗНІТИ СТОРОННЄ НАВАНТАЖЕННЯ: Впровадити Platform Engineering та Golden Path для автоматизації CI/CD й K8s."
            elif high_couplings:
                verdict = "ОБ'ЄДНАТИ СЕРВІСИ (MERGE): Злити зачеплені сервіси у єдиний Модульний Моноліт."
            else:
                verdict = "РОЗДІЛИТИ КОМАНДУ: Додати ще одну Stream-aligned команду."
        else:
            zone = "RED (Когнітивна катастрофа)"
            verdict = "НЕГАЙНИЙ АРХІТЕКТУРНИЙ РЕФАКТОРИНГ: Система не вміщується в головах розробників! Виділити Complicated Subsystem та спростити інфраструктуру."

        return {
            "team": self.telemetry.team_name,
            "cli": final_cli,
            "cli_base": round(cli_base, 2),
            "zone": zone,
            "scores": {"domain": d_avg, "extraneous": e_avg, "communication": c_avg},
            "git_metrics": {
                "services_per_engineer": round(svc_per_eng, 2),
                "high_coupling_pairs": high_couplings,
                "oncall_alerts": self.telemetry.oncall_alerts_per_week
            },
            "penalties_applied": penalty_reasons,
            "verdict": verdict
        }

# --- Демонстраційний запуск для системи Digital Homes ---
if __name__ == "__main__":
    # Сценарій: Команда з 5 осіб тримає 9 мікросервісів
    dh_survey = SurveyScores(
        domain_q=[4.0, 3.8, 4.2, 4.5],      # Декілька незамінних людей, складний домен
        extraneous_q=[4.8, 4.5, 4.2, 4.6],  # Ручний YAML, складна спостережність, часті нічні виклики
        comm_q=[3.5, 4.0, 4.2, 3.8]         # Довгі PR, локрокові релізи
    )

    # Вибірка комітів: показує, які сервіси мінялися разом у межах одного коміту
    commit_samples = [
        ["DeviceService", "TelemetryService"],
        ["AutomationService", "DeviceService"],
        ["DeviceService", "TelemetryService"],  # Зачеплення Device <-> Telemetry
        ["VideoService"],
        ["BillingService"],
        ["AutomationService", "DeviceService"],  # Зачеплення Automation <-> Device
        ["DeviceService", "TelemetryService"],
        ["OTAUpdateService", "DeviceService"]
    ]

    dh_telemetry = GitRepositoryTelemetry(
        team_name="Digital Homes Core Team",
        engineer_count=5,
        active_services_count=9,
        commit_history_sample=commit_samples,
        pr_lead_time_avg_hours=52.0,
        oncall_alerts_per_week=9.5
    )

    auditor = CognitiveLoadAuditor(dh_survey, dh_telemetry)
    report = auditor.evaluate()

    print(f"=== ЗВІТ АУДИТУ КОГНІТИВНОГО НАВАНТАЖЕННЯ: {report['team']} ===")
    print(f"Індекс CLI: {report['cli']} / 5.0 (Базовий: {report['cli_base']})")
    print(f"Зона ризику: {report['zone']}")
    print(f"Компоненти балів: {report['scores']}")
    print(f"Сервісів на інженера: {report['git_metrics']['services_per_engineer']}")
    print(f"Виявлені штрафи: {report['penalties_applied']}")
    print(f"\nАРХІТЕКТУРНИЙ ВЕРДИКТ:\n -> {report['verdict']}")
