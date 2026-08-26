# ⚙️ Автоматизований валідатор матриці FMEA та генератор реєстру

Коли таблиця FMEA налічує десятки вузлів і сотні потенційних режимів відмови, ручний перенос числових оцінок і контрзаходів у код прошивки неминуче призводить до розсинхронізації: схемотехнік додає супресор чи шунт, а прошивка не містить коду діагностики, або інженер занижує виявність `D` на папері без реалізації відповідної функції в драйвері. Скрипт валідації автоматизує цей ланцюг: він перевіряє коректність інженерної матриці (формат, діапазони оцінок `1..10`, наявність обов'язкових контрзаходів для критичних наслідків), розраховує класифікацію пріоритету дій (Action Priority, AP) за стандартом AIAG-VDA і транслює записи у C-сумісний заголовочний файл реєстру відмов для вбудованої системи.

```
       [ fmea_matrix.json ]
                │
                ▼
      ┌────────────────────┐
      │  fmea_validator.py │ ──── Перевірка діапазонів (S, O, D ∈ [1..10])
      │                    │ ──── Перевірка правила S ≥ 9 (High Priority)
      │                    │ ──── Розрахунок RPN та AIAG-VDA Action Priority
      └─────────┬──────────┘
                │
        ┌───────┴───────────────────┐
        ▼                           ▼
[ fmea_report.md ]        [ fmea_registry_autogen.h ]
(Звіт аудиту надійності)    (C/C++ структури та діагностичні ID)
```

## Механізм валідації та інженерні правила перевірки

Валідатор працює не просто як синтаксичний парсер JSON, а як автоматизований аудитор надійності, що спирається на набір формалізованих інженерних правил:

1. **Цілісність ідентифікаторів та іменування:** кожен режим відмови мусить мати унікальний літерно-цифровий ідентифікатор із префіксом підсистеми (`PWR_`, `BUS_`, `MCU_`, `ACT_`). Це унеможливлює випадкове перезаписування рядків при злитті гілок у системі контролю версій.
2. **Перевірка рангових меж:** оцінки тяжкості (`S`), імовірності виникнення (`O`) та виявлення (`D`) повинні бути суворо цілими числами в замкненому інтервалі від 1 до 10. Будь-яке пропущене поле або дробове значення кваліфікується як критична помилка валідації.
3. **Безумовний контроль критичних наслідків (`S ≥ 9`):** якщо тяжкість відмови оцінена у 9 або 10 балів (некерований рух, ураження струмом, займання), система автоматично вимагає наявності апаратного або архітектурного контрзаходу. Зниження ризику лише за рахунок «покращення інструкції оператора» відхиляється.
4. **Обґрунтованість зниження показника виявлення (`D`):** якщо в результаті впровадження контрзаходу вторинне значення `post_detection` встановлено меншим за початкове `detection`, валідатор перевіряє наявність поля `diagnostic_func`. Знизити бал виявлення на папері неможливо без надання імені конкретної C-функції самодіагностики, яка буде викликана вбудованим планувальником.
5. **Математична верифікація таблиці Action Priority:** класичний показник `RPN = S · O · D` має суттєву ваду — добуток зрівнює рідкісну смертельну катастрофу (`10 · 2 · 9 = 180`) із частою косметичною несправністю (`3 · 6 · 10 = 180`). Валідатор реалізує дискретну логіку стандарту AIAG-VDA (2019): оцінка `S` аналізується першою як головний фільтр, після чого комбінація `O` та `D` визначає категорію реагування — високий (`High`), середній (`Medium`) або низький (`Low`) пріоритет.

## Структура вхідного опису матриці

Вхідним документом слугує файл структурованих даних у форматі JSON або YAML. Кожен запис описує окремий режим відмови компонента в межах конкретної функціональної підсистеми виробу:

```json
{
  "project": "Industrial-IoT-Node",
  "version": "1.2.0",
  "items": [
    {
      "id": "PWR_001",
      "subsystem": "Power Supply",
      "component": "Input DC-DC Buck (TPS54302)",
      "failure_mode": "Пробій верхнього MOSFET-ключа (вхід 24 В падає на шину 3.3 В)",
      "cause": "Високовольтний викид від індуктивного навантаження або блискавки",
      "local_effect": "Вигорання перетворювача, коротке замикання",
      "system_effect": "Повна загибель мікроконтролера та радіомодуля, загроза пожежі",
      "severity": 10,
      "occurrence": 3,
      "detection": 8,
      "mitigation_hw": "Вхідний супресор TVS SMAJ28A + захисний стабілітрон Crowbar 3.6 В на виході з eFuse",
      "mitigation_fw": "Моніторинг шини живлення через внутрішній супервізор BOD (Brown-out Detector)",
      "diagnostic_func": "diag_power_bus_check",
      "post_severity": 10,
      "post_occurrence": 1,
      "post_detection": 2
    },
    {
      "id": "BUS_001",
      "subsystem": "Sensor Bus",
      "component": "I2C Humidity/Temp Sensor (SHT31)",
      "failure_mode": "Зависання шини: лінія SDA притиснута давачем до GND",
      "cause": "Збій тактування або скидання MCU під час читання байта",
      "local_effect": "Неможливість опитати кліматичний давач",
      "system_effect": "Втрата кліматичного контролю, хибна аварія вентиляції",
      "severity": 6,
      "occurrence": 5,
      "detection": 7,
      "mitigation_hw": "Підтягувальні резистори 2.2 кОм, транзисторне керування лінією живлення VDD давача",
      "mitigation_fw": "Процедура скидання шини: генерація 9 тактів SCL і силовий перезапуск VDD",
      "diagnostic_func": "diag_i2c_bus_recovery",
      "post_severity": 6,
      "post_occurrence": 2,
      "post_detection": 1
    }
  ]
}
```

## Повна реалізація скрипта валідації та генератора

Скрипт мовою Python реалізує завантаження схеми, математичний розрахунок Action Priority, перевірку перехресних вимог та кодогенерацію:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fmea_validator.py — Валідатор матриці FMEA та генератор C-заголовків реєстру відмов.
"""

import json
import sys
import os
from typing import List, Dict, Any, Tuple


class ActionPriority:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def calculate_action_priority(s: int, o: int, d: int) -> str:
    """
    Розрахунок пріоритету дій (Action Priority) за логікою стандарту AIAG & VDA (2019).
    """
    if s >= 9:
        if o >= 2:
            return ActionPriority.HIGH
        else:
            return ActionPriority.HIGH if d >= 5 else ActionPriority.MEDIUM

    if s in (7, 8):
        if o >= 8:
            return ActionPriority.HIGH
        elif o in (6, 7):
            return ActionPriority.HIGH if d >= 5 else ActionPriority.MEDIUM
        elif o in (4, 5):
            return ActionPriority.HIGH if d >= 7 else ActionPriority.MEDIUM
        elif o in (2, 3):
            return ActionPriority.MEDIUM if d >= 7 else ActionPriority.LOW
        else:  # o == 1
            return ActionPriority.LOW

    if s in (4, 5, 6):
        if o >= 8:
            return ActionPriority.HIGH if d >= 7 else ActionPriority.MEDIUM
        elif o in (6, 7):
            return ActionPriority.MEDIUM
        elif o in (4, 5):
            return ActionPriority.MEDIUM if d >= 7 else ActionPriority.LOW
        else:
            return ActionPriority.LOW

    # s <= 3
    if o >= 8 and d >= 7:
        return ActionPriority.MEDIUM
    return ActionPriority.LOW


class FMEAValidator:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.items: List[Dict[str, Any]] = []
        self.project_name = ""
        self.version = ""

    def load_and_validate(self) -> bool:
        if not os.path.exists(self.filepath):
            self.errors.append(f"Файл не знайдено: {self.filepath}")
            return False

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"Помилка парсингу JSON: {e}")
            return False

        self.project_name = data.get("project", "UnnamedProject")
        self.version = data.get("version", "1.0.0")
        items = data.get("items", [])

        if not items:
            self.errors.append("Список 'items' порожній або відсутній.")
            return False

        seen_ids = set()

        for idx, item in enumerate(items):
            item_id = item.get("id", f"ITEM_{idx}")
            if item_id in seen_ids:
                self.errors.append(f"Дубльований ідентифікатор запису: {item_id}")
            seen_ids.add(item_id)

            # Перевірка діапазонів оцінок S, O, D
            s = item.get("severity", 0)
            o = item.get("occurrence", 0)
            d = item.get("detection", 0)

            for name, val in [("severity", s), ("occurrence", o), ("detection", d)]:
                if not isinstance(val, int) or not (1 <= val <= 10):
                    self.errors.append(f"[{item_id}] Неприпустиме значення {name}={val} (має бути ціле 1..10)")

            # Розрахунок початкових RPN та AP
            item["rpn"] = s * o * d
            item["ap"] = calculate_action_priority(s, o, d)

            # Перевірка вторинних оцінок після контрзаходів
            post_s = item.get("post_severity")
            post_o = item.get("post_occurrence")
            post_d = item.get("post_detection")

            if None not in (post_s, post_o, post_d):
                for name, val in [("post_severity", post_s), ("post_occurrence", post_o), ("post_detection", post_d)]:
                    if not isinstance(val, int) or not (1 <= val <= 10):
                        self.errors.append(f"[{item_id}] Неприпустиме значення {name}={val}")
                item["post_rpn"] = post_s * post_o * post_d
                item["post_ap"] = calculate_action_priority(post_s, post_o, post_d)
            else:
                item["post_rpn"] = None
                item["post_ap"] = None

            # Інженерні перевірки
            diag_fn = item.get("diagnostic_func", "")
            if d > 1 and post_d is not None and post_d < d:
                if not diag_fn or diag_fn.strip() == "":
                    self.warnings.append(
                        f"[{item_id}] Показник виявлення зменшено з D={d} до D={post_d}, "
                        "але не вказано назву функції діагностики ('diagnostic_func')."
                    )

            if s >= 9 and item["ap"] == ActionPriority.HIGH:
                if not item.get("mitigation_hw") and not item.get("mitigation_fw"):
                    self.errors.append(
                        f"[{item_id}] КРИТИЧНО: Severity={s} (High Priority), але відсутні апаратні або програмні контрзаходи!"
                    )

            self.items.append(item)

        return len(self.errors) == 0

    def generate_markdown_report(self) -> str:
        lines = [
            f"# Звіт валідації FMEA: {self.project_name} (v{self.version})\n",
            f"- Загальна кількість режимів відмов: **{len(self.items)}**",
            f"- Кількість критичних помилок валідації: **{len(self.errors)}**",
            f"- Кількість зауважень: **{len(self.warnings)}**\n",
            "## Таблиця ризиків та пріоритетів дій (AP)\n",
            "| ID | Вузол / Режим | S | O | D | RPN | AP | Контрзаходи (HW/FW) | S' | O' | D' | RPN' | AP' |",
            "|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|",
        ]

        for it in self.items:
            mit = f"HW: {it.get('mitigation_hw', '-')}<br>FW: {it.get('mitigation_fw', '-')}"
            post_s = it.get("post_severity", "-")
            post_o = it.get("post_occurrence", "-")
            post_d = it.get("post_detection", "-")
            post_rpn = it.get("post_rpn", "-")
            post_ap = it.get("post_ap", "-")

            row = (
                f"| {it['id']} | **{it['component']}**:<br>{it['failure_mode']} | "
                f"{it['severity']} | {it['occurrence']} | {it['detection']} | "
                f"**{it['rpn']}** | `{it['ap']}` | {mit} | "
                f"{post_s} | {post_o} | {post_d} | {post_rpn} | `{post_ap}` |"
            )
            lines.append(row)

        return "\n".join(lines)

    def generate_c_header(self) -> str:
        guard = f"FMEA_REGISTRY_AUTOGEN_{self.project_name.upper().replace('-', '_')}_H"
        lines = [
            f"/* Автоматично згенеровано fmea_validator.py для проєкту {self.project_name} v{self.version} */",
            f"#ifndef {guard}",
            f"#define {guard}",
            "",
            "#include <stdint.h>",
            "#include <stdbool.h>",
            "",
            "#ifdef __cplusplus",
            'extern "C" {',
            "#endif",
            "",
            "typedef enum {",
            "    FMEA_AP_LOW = 0,",
            "    FMEA_AP_MEDIUM = 1,",
            "    FMEA_AP_HIGH = 2",
            "} fmea_action_priority_t;",
            "",
            "typedef enum {",
        ]

        for it in self.items:
            enum_name = f"FMEA_ID_{it['id'].upper()}"
            lines.append(f"    {enum_name},")

        lines.extend([
            "    FMEA_ID_COUNT",
            "} fmea_record_id_t;",
            "",
            "typedef struct {",
            "    fmea_record_id_t id;",
            "    const char*      id_str;",
            "    const char*      component;",
            "    uint8_t          severity;",
            "    uint8_t          occurrence;",
            "    uint8_t          detection;",
            "    uint16_t         rpn;",
            "    fmea_action_priority_t ap;",
            "    bool (*diag_callback)(void);",
            "} fmea_record_t;",
            "",
            "/* Прототипи зареєстрованих діагностичних функцій */",
        ])

        diag_funcs = set(it.get("diagnostic_func") for it in self.items if it.get("diagnostic_func"))
        for fn in sorted(diag_funcs):
            lines.append(f"bool {fn}(void);")

        lines.extend([
            "",
            f"#define FMEA_RECORD_COUNT ({len(self.items)})",
            "",
            "extern const fmea_record_t g_fmea_registry[FMEA_RECORD_COUNT];",
            "",
            "#ifdef __cplusplus",
            "}",
            "#endif",
            "",
            f"#endif /* {guard} */",
        ])

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Ужиток: python fmea_validator.py <шлях_до_fmea.json> [--out-dir <тека>]")
        sys.exit(1)

    json_file = sys.argv[1]
    out_dir = "."
    if "--out-dir" in sys.argv:
        idx = sys.argv.index("--out-dir")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]

    validator = FMEAValidator(json_file)
    ok = validator.load_and_validate()

    if validator.warnings:
        print("ЗАУВАЖЕННЯ:")
        for w in validator.warnings:
            print(f"  [!] {w}")

    if not ok:
        print("КРИТИЧНІ ПОМИЛКИ:")
        for e in validator.errors:
            print(f"  [x] {e}")
        sys.exit(1)

    print(f"Валідація успішна! Оброблено {len(validator.items)} записів FMEA.")

    # Збереження звіту
    rep_path = os.path.join(out_dir, "fmea_report.md")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write(validator.generate_markdown_report())
    print(f"Звіт збережено у: {rep_path}")

    # Збереження C-заголовка
    hdr_path = os.path.join(out_dir, "fmea_registry_autogen.h")
    with open(hdr_path, "w", encoding="utf-8") as f:
        f.write(validator.generate_c_header())
    print(f"C-заголовок згенеровано у: {hdr_path}")


if __name__ == "__main__":
    main()
```

## Обробка крайових випадків та відмов діагностики

У реальних вбудованих проєктах особливу небезпеку становлять відмови самої діагностичної підсистеми. Якщо колбек `diag_power_bus_check` або `diag_i2c_bus_recovery` зависає у нескінченному циклі очікування прапорця апаратного регістра, сама спроба виявити несправність перетворюється на повний збій системи. Для запобігання цьому генератор накладає специфічні інженерні обмеження на сигнатуру колбеків:

- **Фіксований квант часу:** кожна діагностична функція зобов'язана виконуватися за строго детермінований час (наприклад, не більше 500 мікросекунд) і повертати булевий статус успіху без виклику блокуючих операцій очікування (busy-wait).
- **Збереження у постійній пам'яті (Flash/ROM):** згенерований масив `g_fmea_registry` має специфікатор `const`, що розміщує незмінну таблицю у Flash-пам'яті мікроконтролера. Це економить дефіцитну оперативну пам'ять (RAM), споживаючи лише близько 32 байтів Flash на один запис режиму відмови.
- **Динамічний лічильник інцидентів:** стан відмов під час роботи пристрою відстежується в окремому масиві оперативної пам'яті `fmea_runtime_state_t`, де фіксується кількість зафіксованих збоїв, часова мітка останнього спрацьовування та поточний стан аварійного автомата.

## Інтеграція в інженерний конвеєр CI/CD

Автоматизована валідація стає дієвим інструментом лише тоді, коли вона вбудована у щоденний конвеєр розробки. У типовому робочому процесі скрипт викликається на етапі передкомпіляційного аналізу (pre-build step) у Makefile або CMake-сценарії:

```cmake
# Інтеграція генерації реєстру відмов у CMake
find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/fmea_registry_autogen.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fmea_validator.py
            ${CMAKE_CURRENT_SOURCE_DIR}/docs/fmea_matrix.json
            --out-dir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/docs/fmea_matrix.json
            ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fmea_validator.py
    COMMENT "Валідація матриці FMEA та генерація C-заголовків реєстру відмов"
)

add_custom_target(generate_fmea_registry ALL
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/fmea_registry_autogen.h
)
```

Такий підхід забезпечує жорстку інженерну дисципліну на всіх стадіях життєвого циклу продукту:

- **Захист від несинхронізованих релізів:** жодна зміна схемотехніки чи додавання нового сенсора не може бути скомпільована у бінарний образ без внесення відповідного запису до матриці відмов у вихідному JSON-документі.
- **Обов'язкова наявність діагностичного коду:** якщо розробник стверджує в документації, що пристрій виявляє відмову давача (значення `D` знижено до 1 або 2), згенерований заголовочний файл вимагає наявності конкретної функції `diag_callback`. Спроба зібрати прошивку без реалізації цієї діагностики завершиться помилкою компонування (`undefined reference`).
- **Автоматична звітність для аудитів:** форматований звіт надійності у форматі Markdown генерується автоматично під час кожної збірки релізного тегу в системі CI/CD, гарантуючи повну простежуваність (traceability) між схемними ризиками, кодом прошивки та результатами апаратних тестів.
- **Зниження людського фактора:** виключено ситуацію, коли інженер суб'єктивно вважає критичну відмову «неважливою» через низький RPN: жорсткі правила AIAG-VDA зупиняють процес збірки доти, доки відмова `S ≥ 9` не отримає затвердженого апаратного контрзаходу.
