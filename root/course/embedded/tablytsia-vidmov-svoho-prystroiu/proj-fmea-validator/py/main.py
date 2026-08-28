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
