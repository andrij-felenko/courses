# Калькулятор бюджету часу та вартості апаратної ревізії

У розробці електроніки кожна апаратна ітерація друкованої плати (англ. *PCB respin*) є компромісом між часом виходу продукту на ринок (Time-to-Market), прямими фінансовими витратами на виробництво та непрямими збитками від простою інженерної команди. Коли під час першого увімкнення прототипу (Bring-up) виявляється критична помилка, керівник проєкту та провідний інженер постають перед вибором:
1. Замовити нову ревізію плати за стандартним виробничим циклом (дешево, але довго).
2. Сплатити за прискорене виготовлення (Fast-turn) і термінову авіадоставку (у 2–4 рази дорожче, але рятує графік).
3. Провести лабораторну «хірургію» (різання доріжок, перемички bodge wire, монтаж dead bug) для відновлення працездатності поточних зразків на столі розробників прошивки.

Щоб приймати це рішення на основі точних чисел, а не інтуїції, створено цей інструмент розрахунку бюджету ітерації.

---

### Математична модель витрат на ревізію

Загальні фінансові витрати на одну апаратну ревізію складаються з двох принципово різних категорій: **прямих виробничих витрат** (матеріали, послуги фабрики, логістика) та **непрямих витрат від простою команди** (фонд оплати праці розробників за час блокування заліза).

Повна вартість апаратної ітерації описується формулою:

```
C_total = C_fab + C_smt + C_parts + C_shipping + C_downtime
```

де складові визначаються фізичними та організаційними факторами:

1. **`C_fab` (Вартість виготовлення голих плат):**
   Включає базову вартість фотолітографії, підготовки фотошаблонів, травлення міді, ламінування багатошарового пакету (FR-4, препрег), свердління отворів, гальванічної металізації перехідних отворів (PTH), нанесення паяльної маски та фінішного покриття (HASL, ENIG). При виборі послуги швидкого виробництва (Fast-turn 24h/48h) фабрика застосовує підвищувальний коефіцієнт від `2.5×` до `4.0×` за позачергове обслуговування.

2. **`C_smt` (Вартість автоматизованого монтажу):**
   Складається з фіксованої плати за підготовку виробництва (NRE — Non-Recurring Engineering), виготовлення лазерного трафарету з нержавіючої сталі SUS304 (типово 100–130 мкм завтовшки), калібрування живильників (Feeders) автомата Pick-and-Place, нанесення паяльної пасти, оплавлення в конвеєрній печі та автоматичного оптичного контролю (AOI). Якщо на платі є компоненти у безвивідних корпусах (QFN з центральним термалпадом або BGA), додається вартість рентгенівського контролю (AXI).

3. **`C_parts` (Вартість списання компонентів):**
   При виявленні фатального дефекту змонтовані на бракованій платі компоненти зазвичай не підлягають демонтажу: вартість випоювання, очищення від припою та повторного калібрування перевищує вартість нових деталей, а ризик прихованої теплової деградації кристалів робить їхнє повторне використання небезпечним. Сюди ж додається втрата компонентів у технологічних заправних хвостах (Leader/Trailer) обрізків стрічок (Cut Tape).

4. **`C_shipping` (Логістика та митне оформлення):**
   Вартість міжнародного експрес-авіаперевезення (DHL Express, FedEx Priority) для партії прототипів разом із брокерськими послугами та ввізним митом.

5. **`C_downtime` (Фінансовий еквівалент простою інженерів):**
   Ключовий фактор, який часто ігнорують початківці. Якщо над проєктом працює команда програмістів вбудованого ПЗ, алгоритмістів і тестувальників, відсутність робочого фізичного зразка блокує розробку драйверів периферії, налагодження Bring-up і перевірку радіотракту:

```
C_downtime = N_engineers * Daily_Rate * Delay_Days * Blocking_Factor
```

Тут `Blocking_Factor` (коефіцієнт блокування) лежить у межах від `0.0` (якщо розробка може повноцінно тривати на девбордах чи в симуляторі) до `1.0` (якщо вся команда повністю паралізована через неробочу шину живлення або переплутаний інтерфейс).

Загальний час циклу ітерації в календарних днях:

```
T_total = T_cad + T_dfm + T_fab + T_smt + T_logistics + T_bringup
```

---

### Критерії вибору між лабораторним ремонтом і новим замовленням

Перш ніж братися за скальпель або оформлювати замовлення нової ревізії Rev B, інженер повинен оцінити фізичну здійсненність ручного ремонту за трьома критичними критеріями:

| Тип апаратної проблеми | Можливість ручного ремонту (Bodge Surgery) | Рекомендована дія |
|---|---|---|
| **Переплутані RX/TX або цифрові лінії (GPIO, SPI CS)** | Висока (10–30 хв на плату). Подвійний різ доріжки скальпелем + тонкий емальдріт 0.1 мм. | Лабораторний ремонт для негайного розблокування команди + плановий Rev B. |
| **Неправильна цокольовка LDO або транзистора (SOT-23)** | Середня (30–60 хв). Вигинання ніжок, переворот «на спину» або підпайка дротами. | Лабораторний ремонт на 1–2 прототипах для перевірки прошивки. |
| **Забуті резистори підтяжки (I2C Pull-up, Reset)** | Дуже висока (5–10 хв). Напаювання SMD резисторів 0603/0402 безпосередньо між пінами. | Лабораторний монтаж навісних компонентів. |
| **Помилка у внутрішніх шарах під BGA-чипом** | Нульова. Доріжки та перехідні отвори фізично недоступні під масивом кульок припою. | Негайне скасування/перевипуск через Fast-turn. Ручний ремонт неможливий. |
| **Фатальна помилка RF-тракту (50 Ом лінія 2.4/5 ГГц)** | Вкрай низька. Будь-яка перемичка внесе паразитну індуктивність і зруйнує узгодження. | Перевипуск плати. Ручна перемичка зробить радіотракт неробочим. |

---

### Програмна реалізація калькулятора (Python)

Нижче наведено консольну утиліту для моделювання часових і фінансових витрат. Скрипт розраховує три паралельні сценарії: стандартне перезамовлення, прискорений запуск (Fast-Turn) і лабораторне виправлення перемичками з паралельним замовленням виправленої ревізії.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Калькулятор часових та фінансових витрат на апаратну ітерацію друкованої плати.

Моделює прямі витрати на виробництво, логістику та вартість простою інженерної
команди для різних сценаріїв подолання апаратної помилки.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class IterationConfig:
    board_name: str
    layer_count: int
    board_qty: int
    pcb_area_cm2: float
    bom_cost_per_board: float
    smd_parts_count: int
    bga_qfn_present: bool

    # Інженерна команда
    team_size_engineers: int
    engineer_monthly_salary_usd: float
    blocking_factor: float  # 0.0 (не блокує) .. 1.0 (повний блок)


@dataclass
class ScenarioResult:
    name: str
    calendar_days: int
    fab_cost: float
    smt_cost: float
    parts_scrap_cost: float
    shipping_cost: float
    downtime_cost: float
    total_cost: float
    description: str


class IterationCostCalculator:
    WORKING_DAYS_PER_MONTH = 21.0
    WORKING_HOURS_PER_DAY = 8.0

    def __init__(self, config: IterationConfig):
        self.cfg = config
        daily_salary = config.engineer_monthly_salary_usd / self.WORKING_DAYS_PER_MONTH
        self.team_daily_cost = daily_salary * config.team_size_engineers

    def _calc_pcb_fab(self, fast_turn: bool = False) -> tuple[float, int]:
        """Розрахунок вартості та днів фабрикації голої плати."""
        # Базова вартість залежно від кількості шарів
        base_fab = 25.0 if self.cfg.layer_count <= 2 else (60.0 if self.cfg.layer_count <= 4 else 180.0)
        area_factor = max(1.0, self.cfg.pcb_area_cm2 / 100.0)
        qty_factor = max(1.0, self.cfg.board_qty / 5.0)

        cost = base_fab * area_factor * (1.0 + (qty_factor - 1.0) * 0.3)
        days = 4 if self.cfg.layer_count <= 2 else 6

        if fast_turn:
            cost *= 3.2  # Націнка за 24-48 годинне експрес-виробництво
            days = 2

        return round(cost, 2), days

    def _calc_smt_assembly(self, fast_turn: bool = False) -> tuple[float, int]:
        """Розрахунок вартості та днів монтажу SMT."""
        stencil_cost = 20.0
        setup_fee = 40.0 + (30.0 if self.cfg.bga_qfn_present else 0.0)
        per_joint_cost = 0.008
        joints_per_board = self.cfg.smd_parts_count * 2.5
        placement_cost = joints_per_board * per_joint_cost * self.cfg.board_qty

        cost = stencil_cost + setup_fee + placement_cost
        days = 5

        if fast_turn:
            cost *= 2.0
            days = 2

        return round(cost, 2), days

    def evaluate_scenarios(self) -> List[ScenarioResult]:
        results = []

        # ---------------------------------------------------------------------
        # Сценарій 1: Стандартне перевиготовлення (Rev B Standard)
        # ---------------------------------------------------------------------
        cad_days = 2
        dfm_days = 1
        fab_cost, fab_days = self._calc_pcb_fab(fast_turn=False)
        smt_cost, smt_days = self._calc_smt_assembly(fast_turn=False)
        shipping_cost = 45.0
        shipping_days = 6
        bringup_days = 2

        total_days_std = cad_days + dfm_days + fab_days + smt_days + shipping_days + bringup_days
        scrap_cost_std = self.cfg.bom_cost_per_board * self.cfg.board_qty
        downtime_std = (total_days_std * (5.0 / 7.0)) * self.team_daily_cost * self.cfg.blocking_factor

        total_cost_std = fab_cost + smt_cost + scrap_cost_std + shipping_cost + downtime_std

        results.append(ScenarioResult(
            name="1. Повне стандартне перезамовлення (Rev B)",
            calendar_days=total_days_std,
            fab_cost=fab_cost,
            smt_cost=smt_cost,
            parts_scrap_cost=round(scrap_cost_std, 2),
            shipping_cost=shipping_cost,
            downtime_cost=round(downtime_std, 2),
            total_cost=round(total_cost_std, 2),
            description="Стандартна черга фабрики та економна доставка. Мінімальні прямі витрати, але найбільша затримка проєкту."
        ))

        # ---------------------------------------------------------------------
        # Сценарій 2: Термінове прискорене виготовлення (Fast-Turn + Express)
        # ---------------------------------------------------------------------
        cad_days_ft = 1
        dfm_days_ft = 1
        fab_cost_ft, fab_days_ft = self._calc_pcb_fab(fast_turn=True)
        smt_cost_ft, smt_days_ft = self._calc_smt_assembly(fast_turn=True)
        shipping_cost_ft = 140.0
        shipping_days_ft = 3
        bringup_days_ft = 1

        total_days_ft = cad_days_ft + dfm_days_ft + fab_days_ft + smt_days_ft + shipping_days_ft + bringup_days_ft
        scrap_cost_ft = scrap_cost_std
        downtime_ft = (total_days_ft * (5.0 / 7.0)) * self.team_daily_cost * self.cfg.blocking_factor

        total_cost_ft = fab_cost_ft + smt_cost_ft + scrap_cost_ft + shipping_cost_ft + downtime_ft

        results.append(ScenarioResult(
            name="2. Прискорене перезамовлення (Fast-Turn + Courier)",
            calendar_days=total_days_ft,
            fab_cost=fab_cost_ft,
            smt_cost=smt_cost_ft,
            parts_scrap_cost=round(scrap_cost_ft, 2),
            shipping_cost=shipping_cost_ft,
            downtime_cost=round(downtime_ft, 2),
            total_cost=round(total_cost_ft, 2),
            description="24-годинна фабрикація, пріоритетний SMT-монтаж та авіакур'єр DHL/FedEx. Мінімізує час простою команди."
        ))

        # ---------------------------------------------------------------------
        # Сценарій 3: Лабораторний ремонт (Bodge Surgery) + Фоновий стандартний Rev B
        # ---------------------------------------------------------------------
        rework_engineer_hours = 4.0
        rework_labor_cost = (self.cfg.engineer_monthly_salary_usd / (self.WORKING_DAYS_PER_MONTH * self.WORKING_HOURS_PER_DAY)) * rework_engineer_hours
        rework_materials_cost = 5.0  # Емальдріт + УФ-клей

        unblocked_after_days = 1
        downtime_rework = (unblocked_after_days * (5.0 / 7.0)) * self.team_daily_cost * self.cfg.blocking_factor

        total_cost_rework = fab_cost + smt_cost + shipping_cost + rework_labor_cost + rework_materials_cost + downtime_rework

        results.append(ScenarioResult(
            name="3. Лабораторний ремонт (Bodge) + Фоновий Rev B",
            calendar_days=unblocked_after_days,
            fab_cost=fab_cost,
            smt_cost=smt_cost,
            parts_scrap_cost=round(rework_labor_cost + rework_materials_cost, 2),
            shipping_cost=shipping_cost,
            downtime_cost=round(downtime_rework, 2),
            total_cost=round(total_cost_rework, 2),
            description="Плата виправляється скальпелем і перемичками за 4 години. Команда розробників пише прошивку одразу, поки Rev B виготовляється штатно."
        ))

        return results


def print_report(cfg: IterationConfig, results: List[ScenarioResult]):
    print("=" * 80)
    print(f" ЗВІТ АНАЛІЗУ ВИТРАТ НА АПАРАТНУ ІТЕРАЦІЮ: {cfg.board_name}")
    print("=" * 80)
    print(f"Параметри плати: {cfg.layer_count} шари, {cfg.pcb_area_cm2:.1f} см², {cfg.smd_parts_count} SMD деталей, партія {cfg.board_qty} шт.")
    print(f"Команда: {cfg.team_size_engineers} інженерів, зарплата ${cfg.engineer_monthly_salary_usd:.0f}/міс, фактор блокування: {cfg.blocking_factor:.1f}")
    print("-" * 80)

    for res in results:
        print(f"\n▶ {res.name}")
        print(f"  Час до готовності заліза : {res.calendar_days} кал. днів")
        print(f"  Прямі витрати на Fab/SMT : ${res.fab_cost + res.smt_cost:.2f} (Fab: ${res.fab_cost:.2f}, SMT: ${res.smt_cost:.2f})")
        print(f"  Списання деталей / Ремонт: ${res.parts_scrap_cost:.2f}")
        print(f"  Доставка та логістика    : ${res.shipping_cost:.2f}")
        print(f"  ЦІНА ПРОСТОЮ КОМАНДИ     : ${res.downtime_cost:.2f}")
        print(f"  -------------------------------------------------------------")
        print(f"  ПОВНА ВАРТІСТЬ ІТЕРАЦІЇ  : ${res.total_cost:.2f}")
        print(f"  Суть: {res.description}")

    print("\n" + "=" * 80)
    print(" ВИСНОВОК ТА РЕКОМЕНДАЦІЯ:")
    res_std, res_ft, res_bodge = results[0], results[1], results[2]
    savings_vs_std = res_std.total_cost - res_bodge.total_cost
    time_saved_days = res_std.calendar_days - res_bodge.calendar_days

    print(f"• Лабораторний ремонт заощаджує {time_saved_days} днів очікування та ${savings_vs_std:.2f} бюджету за рахунок усунення простою.")
    if cfg.bga_qfn_present and cfg.blocking_factor > 0.7:
        print("• УВАГА: На платі присутні BGA/QFN. Якщо помилка знаходиться у внутрішніх шарах під чипом, ручний ремонт неможливий — обирайте Сценарій 2 (Fast-Turn).")
    print("=" * 80)


if __name__ == "__main__":
    # Приклад: 4-шарова IoT-плата шлюзу з контролером ESP32-S3 та Ethernet
    example_config = IterationConfig(
        board_name="IoT Gateway Rev A -> Rev B",
        layer_count=4,
        board_qty=5,
        pcb_area_cm2=65.0,
        bom_cost_per_board=28.50,
        smd_parts_count=145,
        bga_qfn_present=True,
        team_size_engineers=3,
        engineer_monthly_salary_usd=2500.0,
        blocking_factor=0.85
    )

    calculator = IterationCostCalculator(example_config)
    analysis = calculator.evaluate_scenarios()
    print_report(example_config, analysis)
```

---

### Розбір практичного прикладу розрахунку

Розгляньмо результати моделювання для типового чотиришарового пристрою з переліком із 145 компонентів і командою з трьох інженерів (два програмісти вбудованого ПЗ та один інженер-схемотехнік):

```
================================================================================
 ЗВІТ АНАЛІЗУ ВИТРАТ НА АПАРАТНУ ІТЕРАЦІЮ: IoT Gateway Rev A -> Rev B
================================================================================
Параметри плати: 4 шари, 65.0 см², 145 SMD деталей, партія 5 шт.
Команда: 3 інженерів, зарплата $2500/міс, фактор блокування: 0.85
--------------------------------------------------------------------------------

▶ 1. Повне стандартне перезамовлення (Rev B)
  Час до готовності заліза : 22 кал. днів
  Прямі витрати на Fab/SMT : $164.50 (Fab: $60.00, SMT: $104.50)
  Списання деталей / Ремонт: $142.50
  Доставка та логістика    : $45.00
  ЦІНА ПРОСТОЮ КОМАНДИ     : $4770.41
  -------------------------------------------------------------
  ПОВНА ВАРТІСТЬ ІТЕРАЦІЇ  : $5122.41
  Суть: Стандартна черга фабрики та економна доставка.

▶ 2. Прискорене перезамовлення (Fast-Turn + Courier)
  Час до готовності заліза : 10 кал. днів
  Прямі витрати на Fab/SMT : $401.00 (Fab: $192.00, SMT: $209.00)
  Списання деталей / Ремонт: $142.50
  Доставка та логістика    : $140.00
  ЦІНА ПРОСТОЮ КОМАНДИ     : $2168.37
  -------------------------------------------------------------
  ПОВНА ВАРТІСТЬ ІТЕРАЦІЇ  : $2851.87
  Суть: 24-годинна фабрикація, пріоритетний SMT-монтаж та авіакур'єр.

▶ 3. Лабораторний ремонт (Bodge) + Фоновий Rev B
  Час до готовності заліза : 1 кал. днів
  Прямі витрати на Fab/SMT : $164.50 (Fab: $60.00, SMT: $104.50)
  Списання деталей / Ремонт: $64.52
  Доставка та логістика    : $45.00
  ЦІНА ПРОСТОЮ КОМАНДИ     : $216.84
  -------------------------------------------------------------
  ПОВНА ВАРТІСТЬ ІТЕРАЦІЇ  : $490.86
  Суть: Плата виправляється скальпелем і перемичками за 4 години.
================================================================================
```

---

### Головні інженерні висновки з моделі

1. **Прямі витрати на склотекстоліт оманливі.** Замовлення п'яти плат за $60 виглядає незначним, але 22 дні очікування при блокуванні трьох фахівців коштують проєкту **майже $4800** тільки у фонді оплати праці.
2. **Fast-Turn окупається миттєво.** Сплата потрійної ціни за термінове виготовлення та авіакур'єра додає ~$350 прямих витрат, але скорочує простій на 12 днів, що дає чисту економію понад $2200.
3. **Хірургія перемичками — абсолютний чемпіон за ефективністю.** Якщо дефект можна виправити перерізанням трьох доріжок і запайкою трьох емальованих провідників (0.1 мм) під мікроскопом за пів дня, команда продовжує роботу без простою. При цьому чиста ревізія Rev B замовляється у фоновому режимі без переплат за терміновість.
4. **Гібридна стратегія є стандартом індустрії.** Досвідчені апаратні команди ніколи не обирають між «лише чекати» або «лише паяти»: вони негайно лагодять 1–2 зразки для програмістів, паралельно виправляють CAD-файли та відправляють виправлену версію на фабрику в той самий день.
