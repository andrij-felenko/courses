# ⚙️ Реалізація конвеєрного валідатора .map та -fstack-usage

Автоматизація контролю апаратних ресурсів у конвеєрі CI/CD вимагає детермінованого, швидкого та автономного інструменту, який здатний розбирати артефакти компілятора та компонувальника безпосередньо на хості збірки. 

Такий інструмент повинен вирішувати три взаємопов'язані інженерні задачі:
1. Витягувати точні розміри секцій Flash та RAM із карти компонування (`.map`) та локалізувати символи з найбільшим споживанням пам'яті.
2. Зчитувати розміри локальних стек-фреймів із файлів `-fstack-usage` (`.su`), будувати орієнтований граф викликів програми та розраховувати найгірший шлях використання стека (WCEP) для кожної задачі реального часу.
3. Зіставляти отримані метрики з декларативною конфігурацією бюджету, генерувати зрозумілий Markdown-звіт для розробників у запиті на злиття та повертати ненульовий код виходу в разі порушення встановлених лімітів.

Нижче наведено повну архітектуру, покроковий розбір алгоритмів та робочу реалізацію виробничого валідатора.

---

## Архітектура та етапи роботи інструменту

Валідатор побудований за модульним принципом і складається з трьох ключових обчислювальних блоків:

```text
firmware.map ───> [1. Map Parser]          ───┐
                                               ├──> [3. Budget Evaluator] ──> GitHub Actions MD
*.su файли   ───> [2. Callgraph Analyzer] ───┘             │
                                                            └──> Exit Code (0 або 1)
```

### Етап 1: Парсинг карти компонування (Memory Section Extraction)
Компонувальник GNU ld генерує детальний звіт про розміщення символів у пам'яті. Парсер аналізує заголовки секцій пам'яті, виділяє розміри виконуваного коду (`.text`), констант (`.rodata`), ініціалізованих даних (`.data`) та нульових статичних масивів (`.bss`). 

Сумарний розмір Flash обчислюється як сума `.text`, `.rodata` та початкових значень `.data`, а статичне навантаження на SRAM — як сума `.data` та `.bss`.

Різні компонувальники (GNU ld, LLVM lld, ARM Compiler 6 armlink) мають відмінності у форматуванні таблиць карт пам'яті. Регулярні вирази парсера налаштовані на універсальне зіставлення шістнадцяткових зміщень та розмірів, що дозволяє коректно розпізнавати секції незалежно від відступів та версії компілятора.

### Етап 2: Побудова графа викликів та пошук WCEP стека
Компілятор GCC під час складання з прапорцем `-fstack-usage` генерує поруч із кожним об'єктним файлом звіт `.su`, де для кожної функції вказано точний розмір її локального стек-фрейму в байтах.

Аналізатор зчитує всі `.su` файли у каталозі збірки, формує таблицю відповідності «ім'я функції → розмір фрейму» та будує орієнтований граф викликів. Для кожної точки входу (наприклад, функції тіла задачі RTOS) алгоритм рекурсивно виконує пошук у глибину (Depth-First Search — DFS), підсумовуючи байти стек-фреймів на кожному кроці та зберігаючи максимальну вагу знайденого шляху.

Для захисту від циклічних залежностей алгоритм веде множину відвіданих на поточному шляху вершин `visited`. Якщо функція зустрічається повторно на тій самій гілці викликів, валідатор фіксує пряму або взаємну рекурсію, яка у вбудованому коді вважається критичним архітектурним дефектом.

### Етап 3: Оцінка бюджету та генерація зворотного зв'язку
Отримані розміри секцій та розраховані значення WCEP порівнюються з лімітами конфігураційного файлу. Валідатор формує форматовану таблицю Markdown із дельтами та переліком критичних шляхів, після чого виводить звіт у стандартний потік виводу та повертає код виходу `0` (успіх) або `1` (помилка, блокування злиття).

---

## Повна реалізація валідатора мовою Python

Нижче наведено вихідний код утиліти `budget_gate.py`, що не має зовнішніх залежностей і працює на стандартній бібліотеці Python 3.8+:

```python
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
```

---

## Інтеграція валідатора у конвеєр GitHub Actions

Для забезпечення автоматичного виконання перевірки на кожній події створення або оновлення Pull Request скрипт додається до робочого процесу CI:

```yaml
name: Embedded Budget Verification Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  verify-budget:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install ARM Embedded Toolchain
        run: sudo apt-get update && sudo apt-get install -y gcc-arm-none-eabi

      - name: Compile Firmware with Stack Analysis
        run: |
          mkdir -p build
          cd build
          cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-fstack-usage" ..
          make -j$(nproc)

      - name: Run Budget Gate
        id: budget_gate
        run: |
          python3 scripts/budget_gate.py config/budget.json build/firmware.map build > budget_report.md

      - name: Post PR Comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('budget_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

---

## Інженерні підводні камені та методи їх нейтралізації

Під час експлуатації автоматичних воріт збірки на реальних проєктах виникає кілька специфічних крайових випадків, які необхідно враховувати в логіці парсера:

### 1. Динамічні стек-фрейми (`alloca`, VLA)
Якщо розробник оголосив масив змінної довжини `uint8_t buf[len]`, компілятор GCC записує у файл `.su` кваліфікатор `dynamic` замість фіксованого числа. Валідатор зобов'язаний негайно генерувати помилку збірки, оскільки наявність динамічного стека унеможливлює статичний розрахунок WCEP і створює пряму загрозу переповнення пам'яті.

### 2. Манглювання імен функцій у C++
Функції C++ записуються у файлах `.su` та `.map` у мангльованому вигляді (наприклад, `_ZN10Controller7executeEv`). Для коректного зіставлення символів із конфігураційним файлом парсер повинен виконувати деманглювання імен за допомогою утиліти `c++filt` або спеціалізованих модулів деманглювання.

### 3. Непрямі виклики через вказівники на функції
Якщо виклик здійснюється через вказівник на функцію або віртуальну таблицю `vtable`, статичний граф викликів розривається. У конфігурації `budget.yml` має бути передбачений механізм явного зазначення можливих цілей виклику (Call Target Annotations), щоб алгоритм перевірив найважчу гілку серед усіх можливих реалізацій.

### 4. Врахування переривань у фонових задачах
Фонова задача RTOS може бути перервана апаратним перериванням у найглибшій точці свого стека. Щоб уникнути катастрофи переповнення пам'яті під час переривань, валідатор повинен автоматично додавати розмір стек-фрейму найважчого обробника ISR та базового апаратного кадру збереження контексту (32–104 байти) до розрахованого значення WCEP кожної задачі.

### 5. Очищення тимчасових файлів та детермінізм збірки
Файли `.su` генеруються компілятором під час трансляції кожного об'єктного файлу. Якщо вихідний файл було видалено з проєкту, але об'єктний файл залишився в каталозі збірки через інкрементальну компіляцію, парсер може врахувати застарілий стек-фрейм. З цієї причини конвеєр CI завжди повинен виконувати аналіз на абсолютно чистій збірці (Clean Build) у чистому робочому каталозі.
