# ⚙️ Практичний аудит когнітивного навантаження команди

Цей інженерний інструментарій містить опитувальник когнітивного навантаження команди, математичний алгоритм розрахунку індексу навантаження (Cognitive Load Index — CLI) та вичерпний Python-скрипт аналізу телеметрії репозиторіїв (зачеплення змін, перемикання контекстів, тривалість PR, навантаження чергування on-call) для ухвалення свідомого рішення про розрозріз або об'єднання сервісів.

---

## 1. Рубрика аудиту: 12 діагностичних питань

Оцінка когнітивного навантаження проводиться гібридним методом, який поєднує **суб'єктивний аналіз ментальних зусиль інженерів** (через анонімне оцінювання) та **об'єктивну телеметрію Git-репозиторіїв та трекерів інцидентів**.

Аудит оцінює три блоки питань за шкалою від 1 (найнижче навантаження / ідеальний стан) до 5 (критичне перевищення когнітивної ємності):

### Блок A: Доменне (внутрішнє) навантаження — Intrinsic Load Score
1. **Онбординг новачків:** Наскільки легко новому інженеру осягнути бізнес-правила домену та почати самостійно випускати продуктовий код за перший місяць? (1 — легко, < 2 тижнів; 5 — критично важко, > 4 місяців).
2. **Щільність доменних концепцій:** Скільки незалежних бізнес-сутностей, машин станів та інваріантів змушений одночасно утримувати в мозоку розробник під час вирішення звичайної продуктової задачі? (1 — 1–2 концепції; 5 — понад 7 концепцій).
3. **Каскадність бізнес-змін:** Наскільки часто зміна в одному бізнес-правилі призводить до непередбачуваних побічних ефектів або зламу логіки у суміжних функціональних блоках? (1 — вкрай рідко; 5 — постійно).
4. **Незамінність експертів (Bus Factor):** Який відсоток коду або доменних правил у зоні відповідальності команди розбирає лише один конкретний інженер («незамінний Василь»)? (1 — 0%, усі знають усе; 5 — > 40% коду є монополією експерта).

### Блок B: Операційне та інфраструктурне (стороннє) навантаження — Extraneous Load Score
5. **Фрагментація репозиторіїв:** Скільки окремих Git-репозиторіїв та конвеєрів CI/CD доводиться регулярно відкривати та правити команді для випуску однієї складеної фічі? (1 — 1 репозиторій; 5 — 4+ репозиторіїв).
6. **Інфраструктурне тертя:** Який відсоток робочого часу інженер витрачає на ручне написання YAML/Docker/Terraform, налагодження конвеєрів CI/CD та налаштування локального середовища? (1 — < 5% часу; 5 — > 35% часу).
7. **Розпорошеність спостережності:** Скільки різних інструментів, вкладок моніторингу та логів (Grafana, Kibana, Jaeger) доводиться вручну зіставляти для розслідування одного продуктового збою? (1 — єдина панель / 1 вкладка; 5 — понад 4 різні інструменти).
8. **Стрес чергування on-call:** Наскільки непередбачуваним та тривожним є чергування on-call для членів команди? (1 — спокійне, 0 нічних викликів; 5 — виснажливе, часті нічні алерти по незнайомих сервісах).

### Блок C: Комунікаційне та контекстне навантаження — Communication & Context Load Score
9. **Міжкомандна координація:** Скільки міжкомандних погоджень, синхронізацій та заявок у Jira вимагає випуск типової зміни в публічному чи внутрішньому API? (1 — нуль, повна автономія; 5 — більше 3 команд).
10. **Поріг перемикання контексту:** Скільки часу розробник витрачає на відновлення ментального контексту після перемикання між різними сервісами чи задачами протягом одного робочого дня? (1 — < 5 хвилин; 5 — > 45 хвилин).
11. **Складність рецензування (PR Latency):** Який середній час очікування рецензування коду (Pull Request) через те, що колеги не розуміють контекст правок у сусідньому сервісі? (1 — < 4 годин; 5 — > 48 годин).
12. **Сynchronized Deployments (Замок релізів):** Наскільки часто реліз сервісу команди вимагає одночасного (локрокового) розгортання сервісів інших команд? (1 — ніколи, повністю незалежний деплой; 5 — постійно).

---

## 2. Алгоритм розрахунку Когнітивного Індексу Команди (CLI)

Математична модель обчислення Cognitive Load Index (CLI) базується на зваженому сумуванні оцінок тривимірної рубрики з додаванням коригувального коефіцієнта об'єктивної телеметрії Git:

```
Score_Domain = (Q1 + Q2 + Q3 + Q4) ÷ 4
Score_Extraneous = (Q5 + Q6 + Q7 + Q8) ÷ 4
Score_Comm = (Q9 + Q10 + Q11 + Q12) ÷ 4

CLI_base = (0.35 · Score_Domain) + (0.45 · Score_Extraneous) + (0.20 · Score_Comm)
```

### Коригування за об'єктивною Git-телеметрією:
Об'єктивна телеметрія розраховується за аналізом комітів та репозиторіїв за останні 90 днів:

1. **Коефіцієнт парного зачеплення змін (Change Coupling Ratio — `C[i,j]`):**
   Частка комітів, які модифікують файли у сервісі A та сервісі B одночасно:

```
C[i,j] = Commits(Svc_i ∩ Svc_j) ÷ Commits(Svc_i)
```

   Якщо `C[i,j] > 0.35`, це свідчить про штучний розріз єдиного контексту. До CLI додається штраф `+0.4`.

2. **Індекс фрагментації володіння (Service-to-Engineer Ratio):**
   Відношення кількості активних сервісів (`N_svc`) до кількості інженерів у Stream-aligned команді (`N_eng`):

```
Ratio = N_svc ÷ N_eng
```

   Якщо `Ratio > 1.5` (наприклад, 8 сервісів на 4 інженерів), до CLI додається штраф `+0.5`.

3. **Підсумкова формула CLI:**

```
CLI = min(5.0,  CLI_base + Penalty_coupling + Penalty_ratio)
```

---

## 3. Практичний Python-скрипт аналізу телеметрії та оцінки меж

Нижче наведено повний виробничий Python-скрипт, який моделює збір опитувальних балів, обчислення `C[i,j]` зачеплення та винесення детального архітектурного вердикту.

```python
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
```

---

## 4. Матриця інженерних рішень за результатами аудиту

На основі розрахованих балів та виявлених джерел навантаження застосовується чітка матриця інженерних рішень:

| Головний фактор навантаження | Виявлений симптом | Неправильний крок (пастка) | **Правильне архітектурне рішення** |
| :--- | :--- | :--- | :--- |
| **Extraneous > 4.0** | Інженери витрачають > 30% часу на Kubernetes, CI/CD та Docker. | Нарізати код на ще дрібніші сервіси. | **Створити Platform Team та розгорнути Golden Path (IDP).** |
| **High Coupling (`C[i,j] > 0.35`)** | Зміна фічі вимагає комітів у 3 репозиторії одночасно. | Написати суворішу інструкцію синхронізації в Jira. | **Об'єднати зачеплені сервіси в один (Merge) або створити Модульний Моноліт.** |
| **Intrinsic > 4.2** | Складна математика, кодеки або аналітика, яку розуміє лише 1 людина. | Змусити всіх інженерів учити вищу математику. | **Виділити складний вузол у Complicated-Subsystem Team.** |
| **Ratio > 1.5** | На 4 інженерів припадає 10 окремих сервісів і 10 конвеєрів. | Найняти ще 10 інженерів у ту саму команду. | **Зменшити кількість сервісів на команду до 2–3 максимум (через злиття).** |

---

## 5. Граничні випадки та ризики хибного оцінювання

Під час проведення аудиту необхідно враховувати три крайові випадки, які можуть викривити результати:

1. **Фаза активного стартапу / прототипування:** На початкових етапах розвитку продукту індекс CLI майже завжди є підвищеним через швидкі зміни домену. Спроба завчасно виділити платформну команду на цьому етапі є **передчасною платформізацією** (Premature Platform).
2. **Зміна складу команди (Turnover):** Якщо склад команди оновився на 50% за останній місяць, високі бали за Блоком A є природним наслідком онбордингу, а не дефектом архітектурного розкрою.
3. **Хибне зачеплення монорепозиторію:** У разі використання монорепозиторію (Monorepo) спільні коміти у конфігураційні файли кореня репо можуть створювати хибне враження високого `C[i,j]`. Алгоритм аналізу мусить фільтрувати правки в інфраструктурних каталогах та аналізувати лише суто доменні вихідні файли.
