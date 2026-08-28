#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автономний валідатор апаратних бюджетів Flash, RAM та стека для CI/CD."""

import os
import re
import sys
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class SectionSummary:
    text: int = 0
    rodata: int = 0
    data: int = 0
    bss: int = 0

    @property
    def flash_total(self) -> int:
        return self.text + self.rodata + self.data

    @property
    def ram_static_total(self) -> int:
        return self.data + self.bss


@dataclass
class StackFrame:
    function_name: str
    frame_size: int
    qualifier: str  # static, dynamic, bounded


class MapFileParser:
    """Парсер карт компонування GNU ld / LLVM lld."""

    def __init__(self, map_path: str):
        self.map_path = map_path

    def parse_sections(self) -> SectionSummary:
        summary = SectionSummary()
        if not os.path.exists(self.map_path):
            raise FileNotFoundError(f"Файл карти пам'яті не знайдено: {self.map_path}")

        patterns = {
            "text": re.compile(r"^\s*\.text\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)", re.MULTILINE),
            "rodata": re.compile(r"^\s*\.rodata\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)", re.MULTILINE),
            "data": re.compile(r"^\s*\.data\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)", re.MULTILINE),
            "bss": re.compile(r"^\s*\.bss\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)", re.MULTILINE),
        }

        with open(self.map_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for sec_name, pattern in patterns.items():
            matches = pattern.findall(content)
            total_size = sum(int(match, 16) for match in matches)
            setattr(summary, sec_name, total_size)

        return summary


class StackUsageAnalyzer:
    """Аналізатор стек-фреймів на базі звітів GCC -fstack-usage."""

    def __init__(self, build_dir: str):
        self.build_dir = build_dir
        self.frames: Dict[str, StackFrame] = {}
        self.call_graph: Dict[str, List[str]] = {}

    def load_su_files(self) -> None:
        """Зчитує всі *.su файли у каталозі збірки."""
        # Формат рядка .su: <file>:<line>:<col>:<function_name>\t<size>\t<qualifier>
        su_pattern = re.compile(r"^([^:]+):(\d+):(\d+):([^\t]+)\t(\d+)\t(\w+)")

        for root, _, files in os.walk(self.build_dir):
            for file in files:
                if file.endswith(".su"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            m = su_pattern.match(line.strip())
                            if m:
                                fn_name = m.group(4).strip()
                                size = int(m.group(5))
                                qual = m.group(6)
                                self.frames[fn_name] = StackFrame(fn_name, size, qual)

    def add_call_edge(self, caller: str, callee: str) -> None:
        if caller not in self.call_graph:
            self.call_graph[caller] = []
        self.call_graph[caller].append(callee)

    def calculate_wcep(self, entry_point: str, visited: Optional[Set[str]] = None) -> Tuple[int, List[str]]:
        """Обчислює найгірший шлях використання стека (WCEP) від точки входу."""
        if visited is None:
            visited = set()

        if entry_point in visited:
            return 0, [f"{entry_point} (RECURSION! Заборонено у вбудованому коді)"]

        visited.add(entry_point)
        current_frame = self.frames.get(entry_point, StackFrame(entry_point, 0, "unknown")).frame_size

        children = self.call_graph.get(entry_point, [])
        if not children:
            visited.remove(entry_point)
            return current_frame, [f"{entry_point} ({current_frame}B)"]

        max_child_cost = 0
        best_path: List[str] = []

        for child in children:
            child_cost, child_path = self.calculate_wcep(child, visited)
            if child_cost > max_child_cost:
                max_child_cost = child_cost
                best_path = child_path

        visited.remove(entry_point)
        total = current_frame + max_child_cost
        return total, [f"{entry_point} ({current_frame}B)"] + best_path


class BudgetGateRunner:
    """Головний модуль верифікації бюджету та формування звіту."""

    def __init__(self, config_path: str, map_path: str, build_dir: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.map_parser = MapFileParser(map_path)
        self.stack_analyzer = StackUsageAnalyzer(build_dir)

    def run(self) -> int:
        summary = self.map_parser.parse_sections()
        self.stack_analyzer.load_su_files()

        max_flash = self.config["limits"]["flash_max_bytes"]
        max_ram = self.config["limits"]["ram_static_max_bytes"]
        task_limits = self.config.get("tasks", {})

        violations = []

        if summary.flash_total > max_flash:
            violations.append(
                f"Flash Overflow: {summary.flash_total} Б перевищує ліміт {max_flash} Б "
                f"(дефіцит: {summary.flash_total - max_flash} Б)"
            )

        if summary.ram_static_total > max_ram:
            violations.append(
                f"RAM Overflow: {summary.ram_static_total} Б перевищує ліміт {max_ram} Б "
                f"(дефіцит: {summary.ram_static_total - max_ram} Б)"
            )

        stack_reports = {}
        for task_name, task_cfg in task_limits.items():
            entry_fn = task_cfg["entry"]
            budget = task_cfg["stack_budget_bytes"]
            cost, path = self.stack_analyzer.calculate_wcep(entry_fn)
            stack_reports[task_name] = (cost, budget, path)
            if cost > budget:
                violations.append(
                    f"Stack Overflow у задачі '{task_name}': WCEP {cost} Б > бюджету {budget} Б"
                )

        self._print_markdown_report(summary, stack_reports, violations)

        if violations:
            print("\n[FAIL] Ворота бюджету заблокували збірку через критичні перевитрати!", file=sys.stderr)
            return 1

        print("\n[SUCCESS] Усі ресурси знаходяться в межах встановленого бюджету.")
        return 0

    def _print_markdown_report(self, s: SectionSummary, stacks: dict, violations: list) -> None:
        print("## 📊 Звіт воріт апаратного бюджету (CI Budget Gate)\n")
        print("| Ресурс | Фактичний розмір | Ліміт бюджету | Використання | Стан |")
        print("|---|---|---|---|---|")
        
        flash_pct = (s.flash_total / self.config["limits"]["flash_max_bytes"]) * 100
        flash_status = "❌ FAIL" if s.flash_total > self.config["limits"]["flash_max_bytes"] else "✅ OK"
        print(f"| **Flash (.text + .rodata + .data)** | {s.flash_total:,} Б | {self.config['limits']['flash_max_bytes']:,} Б | {flash_pct:.1f}% | {flash_status} |")

        ram_pct = (s.ram_static_total / self.config["limits"]["ram_static_max_bytes"]) * 100
        ram_status = "❌ FAIL" if s.ram_static_total > self.config["limits"]["ram_static_max_bytes"] else "✅ OK"
        print(f"| **RAM (.data + .bss)** | {s.ram_static_total:,} Б | {self.config['limits']['ram_static_max_bytes']:,} Б | {ram_pct:.1f}% | {ram_status} |")

        print("\n### 🧵 Стек задач реального часу (WCEP)\n")
        print("| Задача | Найгірший шлях (WCEP) | Бюджет стека | Запас | Стан |")
        print("|---|---|---|---|---|")
        for task, (cost, limit, path) in stacks.items():
            status = "❌ FAIL" if cost > limit else "✅ OK"
            margin = limit - cost
            print(f"| `{task}` | {cost} Б | {limit} Б | {margin} Б | {status} |")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Використання: python budget_gate.py <budget.json> <firmware.map> <build_dir>")
        sys.exit(2)

    runner = BudgetGateRunner(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(runner.run())
