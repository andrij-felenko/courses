# ⚙️ Автоматизований аудит Map-файлу в CI: Python-парсер і контроль лімітів

Коли над мікроконтролерною прошивкою працює команда інженерів, бюджет апаратної пам'яті вичерпується непомітно. Один розробник підтягнув важкий заголовок із неінлайненими шаблонами C++, інший скористався стандартним `sprintf` для швидкого налагодження UART, третій забув ключове слово `const` перед масивом калібрувальних коефіцієнтів, випадково подвоївши навантаження на SRAM та Flash. Локально кожен коміт успішно збирається, але у спільній гілці запас пам'яті тане від релізу до релізу, доки черговий другорядний патч не зламає збірку фатальною помилкою переповнення регіону.

Щоб контролювати бюджет Flash і SRAM на етапі створення пулреквестів, ручного перегляду коду (*code review*) замало: розробник бачить лише текст сирців, але не бачить реальних розмірів секцій, згенерованих компілятором та підтягнутих із системних бібліотек. Надійним захистом є автоматизований аудит Map-файлу компонувальника в конвеєрі неперервної інтеграції (CI/CD).

## Завдання та вимоги до системи аудиту

Виробничий аудит прошивки в автоматизованому конвеєрі вирішує чотири критичні завдання:

1. **Контроль порогів заповнення регіонів пам'яті**:
   Апаратні регіони мікроконтролера (наприклад, Flash на 64 КБ та SRAM на 20 КБ) не повинні заповнюватися до 100%. Для Flash рекомендований поріг попередження становить 85%, а поріг блокування збірки — 90–95% (залишок необхідний для майбутніх оновлень по повітрю OTA або аварійних патчів). Для SRAM поріг має бути ще суворішим — 75–80%, оскільки вільна пам'ять, що залишається після секцій `.data` та `.bss`, використовується динамічно під стек викликів функцій та локальні буфери.

2. **Детекція заборонених символів (*Banned Symbols Check*)**:
   У критичних вбудованих системах діють суворі стандарти надійності (наприклад, MISRA C або IEC 61508), що забороняють використання неконтрольованого динамічного виділення пам'яті (`malloc`, `free`, `operator new`), важких функцій форматування (`_dtoa_r`) або рантайму винятків C++ (`__cxa_throw`, `.ARM.extab`). CI-пайплайн повинен автоматично шукати такі символи у згенерованому бінарнику та відхиляти пулреквест у разі їхньої появи.

3. **Деталізація внеску окремих компонентів і модулів**:
   У разі зростання розміру інженер повинен отримати таблицю з топ-10 найбільших функцій і змінних, згрупованих за об'єктними файлами, щоб миттєво локалізувати причину роздування без ручного читання гігабайтних логів.

4. **Автономність та нульові зовнішні залежності**:
   Скрипт аналізу повинен виконуватися в будь-якому оточенні (локальний комп'ютер, GitHub Actions runner, контейнер Docker на базі Alpine або Debian) за допомогою стандартного інтерпретатора Python 3 без встановлення додаткових пакетів (`pip`).

## Внутрішня механіка парсингу Map-файлу GNU ld

Текстовий формат Map-файлу компонувальника GNU ld має низку специфічних нюансів синтаксису, які необхідно враховувати під час автоматичного розбору:

- **Багаторядковий перенос довгих імен секцій**: якщо ім'я вхідної секції (наприклад, `.text._ZN7Sensors15readCalibrationEv`) разом зі шляхом до об'єктного файлу перевищує фіксовану ширину колонки (зазвичай 28 символів), компонувальник розриває запис на два рядки. Перший рядок містить лише ім'я секції, а наступний рядок із відступом — адресу, розмір та ім'я об'єктного файлу. Парсер повинен коректно склеювати такий контекст через внутрішній стан кінцевого автомата.
- **Фільтрація вирівнювального падінгу (`*fill*`)**: лінкер вставляє байти вирівнювання (2, 4 або 8 байтів) для розміщення функцій на межах слів процесора. Ці записи не є функціями чи змінними і мають враховуватися лише в загальному обсязі зайнятого регіону, але відфільтровуватися зі списку символів.
- **Обчислення розміру несуміжних регіонів**: якщо лінкер-скрипт розміщує таблицю векторів `g_pfnVectors` за адресою `0x08000000`, а основний код `.text` починається з `0x08000400`, розрахунок зайнятого простору повинен базуватися на діапазоні адрес найвищої межі (`high-water mark`), щоб враховувати проміжні порожнечі.

Нижче наведено повний виробничий скрипт на чистому Python, адаптований для запуску в терміналі та CI/CD.

## Реалізація скрипта аудиту: map_audit.py

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map_audit.py — Автономний парсер GNU ld Map-файлу для контролю бюджету пам'яті в CI.
Підтримує перевірку лімітів Flash/RAM, детекцію заборонених символів та експорт у JSON.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional


class SymbolEntry:
    def __init__(self, section: str, address: int, size: int, origin: str):
        self.section = section
        self.address = address
        self.size = size
        self.origin = origin

    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "address": f"0x{self.address:08X}",
            "size_bytes": self.size,
            "origin": self.origin
        }


class MemoryRegion:
    def __init__(self, name: str, origin: int, length: int, attributes: str = ""):
        self.name = name
        self.origin = origin
        self.length = length
        self.attributes = attributes
        self.used_bytes = 0

    @property
    def percentage(self) -> float:
        return (self.used_bytes / self.length * 100.0) if self.length > 0 else 0.0

    @property
    def free_bytes(self) -> int:
        return max(0, self.length - self.used_bytes)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "origin": f"0x{self.origin:08X}",
            "length_bytes": self.length,
            "used_bytes": self.used_bytes,
            "free_bytes": self.free_bytes,
            "percentage": round(self.percentage, 2),
            "attributes": self.attributes
        }


def parse_memory_regions(lines: List[str]) -> Dict[str, MemoryRegion]:
    regions: Dict[str, MemoryRegion] = {}
    in_section = False
    
    # Шаблон рядка: FLASH 0x08000000 0x00010000 xr
    reg_pattern = re.compile(
        r'^\s*([A-Za-z0-9_]+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s*([a-z!]+)?'
    )

    for line in lines:
        if 'Memory Configuration' in line:
            in_section = True
            continue
        if in_section:
            if line.startswith('Linker script and memory map') or line.startswith('Discarded input sections'):
                break
            match = reg_pattern.match(line)
            if match:
                name = match.group(1)
                origin = int(match.group(2), 16)
                length = int(match.group(3), 16)
                attrs = match.group(4) or ""
                if name != '*default*':
                    regions[name] = MemoryRegion(name, origin, length, attrs)
    return regions


def parse_symbols_and_calculate_usage(
    lines: List[str], regions: Dict[str, MemoryRegion]
) -> List[SymbolEntry]:
    symbols: List[SymbolEntry] = []
    in_map = False

    # Регулярні вирази для однорядкового та дворядкового форматів GNU ld
    sec_single_pattern = re.compile(
        r'^\s*(\.[a-zA-Z0-9_\.]+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(.+)$'
    )
    sec_start_pattern = re.compile(r'^\s*(\.[a-zA-Z0-9_\.]+)\s*$')
    sec_cont_pattern = re.compile(r'^\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(.+)$')

    pending_section_name: Optional[str] = None

    for line in lines:
        if 'Linker script and memory map' in line:
            in_map = True
            continue
        if not in_map:
            continue
        if line.startswith('Cross Reference Table') or line.startswith('OUTPUT('):
            break

        # Спроба однорядкового зіставлення
        m_single = sec_single_pattern.match(line)
        if m_single:
            sec_name = m_single.group(1)
            addr = int(m_single.group(2), 16)
            size = int(m_single.group(3), 16)
            origin = m_single.group(4).strip()

            if size > 0 and not origin.startswith('*fill*'):
                symbols.append(SymbolEntry(sec_name, addr, size, origin))
                for reg in regions.values():
                    if reg.origin <= addr < (reg.origin + reg.length):
                        reg.used_bytes = max(reg.used_bytes, (addr + size) - reg.origin)

            pending_section_name = None
            continue

        # Спроба дворядкового зіставлення (початок)
        m_start = sec_start_pattern.match(line)
        if m_start:
            pending_section_name = m_start.group(1)
            continue

        # Спроба дворядкового зіставлення (продовження)
        if pending_section_name:
            m_cont = sec_cont_pattern.match(line)
            if m_cont:
                addr = int(m_cont.group(1), 16)
                size = int(m_cont.group(2), 16)
                origin = m_cont.group(3).strip()

                if size > 0 and not origin.startswith('*fill*'):
                    symbols.append(SymbolEntry(pending_section_name, addr, size, origin))
                    for reg in regions.values():
                        if reg.origin <= addr < (reg.origin + reg.length):
                            reg.used_bytes = max(reg.used_bytes, (addr + size) - reg.origin)
                pending_section_name = None
            else:
                pending_section_name = None

    return symbols


def run_audit(
    map_file: str,
    flash_limit: float,
    ram_limit: float,
    banned_keywords: List[str],
    json_output_path: Optional[str] = None
) -> bool:
    try:
        with open(map_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except OSError as err:
        print(f"[!] ПОМИЛКА читання файлу {map_file}: {err}")
        return False

    regions = parse_memory_regions(lines)
    symbols = parse_symbols_and_calculate_usage(lines, regions)

    print("=" * 78)
    print(f"ЗВІТ АУДИТУ ПАМ'ЯТІ ПРОШИВКИ (GNU ld Map Audit)")
    print(f"Файл: {map_file}")
    print("=" * 78)

    # 1. Стан регіонів пам'яті
    print("\n[1] Апаратні регіони пам'яті:")
    print(f"{'Регіон':<12} {'Початок':<12} {'Розмір (Б)':<12} {'Зайнято (Б)':<12} {'Використання'}")
    print("-" * 78)

    has_violation = False
    for name, reg in regions.items():
        bar_count = int(reg.percentage / 5)
        bar_visual = "█" * bar_count + "░" * (20 - bar_count)
        print(
            f"{name:<12} 0x{reg.origin:08X}   {reg.length:<12} "
            f"{reg.used_bytes:<12} {reg.percentage:6.2f}% [{bar_visual}]"
        )

        limit = flash_limit if ('FLASH' in name.upper() or 'ROM' in name.upper()) else ram_limit
        if reg.percentage > limit:
            print(
                f"  [!] ПОМИЛКА: Регіон '{name}' перевищив допустимий ліміт {limit:.1f}% "
                f"(фактично: {reg.percentage:.2f}%)"
            )
            has_violation = True

    # 2. Топ найбільших символів
    print("\n[2] Топ-10 найбільших функцій та об'єктів за розміром:")
    print(f"{'Розмір (Б)':<12} {'Адреса':<12} {'Секція / Символ':<28} {'Джерело'}")
    print("-" * 78)

    sorted_symbols = sorted(symbols, key=lambda s: s.size, reverse=True)
    for sym in sorted_symbols[:10]:
        print(f"{sym.size:<12} 0x{sym.address:08X}   {sym.section[:26]:<28} {sym.origin}")

    # 3. Перевірка заборонених символів
    print("\n[3] Перевірка заборонених символів (Banned Symbols Check):")
    detected_banned: List[SymbolEntry] = []
    for sym in symbols:
        for keyword in banned_keywords:
            if keyword in sym.section or keyword in sym.origin:
                detected_banned.append(sym)
                break

    if detected_banned:
        for sym in detected_banned:
            print(
                f"  [!] ВИЯВЛЕНО ЗАБОРОНЕНИЙ СИМВОЛ: '{sym.section}' "
                f"({sym.size} байтів) у {sym.origin}"
            )
        has_violation = True
    else:
        print("  [OK] Заборонених символів (динамічна пам'ять, RTTI, винятки) не виявлено.")

    # Експорт у JSON для інтеграції з іншими кроками CI
    if json_output_path:
        report_data = {
            "map_file": map_file,
            "success": not has_violation,
            "regions": {name: reg.to_dict() for name, reg in regions.items()},
            "top_symbols": [s.to_dict() for s in sorted_symbols[:15]],
            "banned_violations": [s.to_dict() for s in detected_banned]
        }
        try:
            with open(json_output_path, 'w', encoding='utf-8') as jf:
                json.dump(report_data, jf, indent=2)
            print(f"\n[INFO] Звіт у форматі JSON успішно збережено в: {json_output_path}")
        except OSError as err:
            print(f"[!] Не вдалося зберегти JSON-звіт: {err}")

    print("\n" + "=" * 78)
    if has_violation:
        print("РЕЗУЛЬТАТ АУДИТУ: ПЕРЕВІРКУ ПРОВАЛЕНО (Збірку зупинено).")
        return False
    else:
        print("РЕЗУЛЬТАТ АУДИТУ: УСПІШНО (Бюджет пам'яті дотримано).")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Автоматичний аудит Map-файлу GNU ld для систем CI/CD."
    )
    parser.add_argument("--map", required=True, help="Шлях до вхідного .map файлу")
    parser.add_argument(
        "--flash-max",
        type=float,
        default=90.0,
        help="Максимальний відсоток заповнення Flash (за замовчуванням: 90.0)"
    )
    parser.add_argument(
        "--ram-max",
        type=float,
        default=80.0,
        help="Максимальний відсоток заповнення RAM (за замовчуванням: 80.0)"
    )
    parser.add_argument(
        "--ban",
        nargs="*",
        default=["malloc", "free", "__cxa_throw", "_dtoa_r", "__udivmoddi4"],
        help="Список заборонених підрядків у назвах символів"
    )
    parser.add_argument(
        "--json",
        default=None,
        help="Опціональний шлях для збереження JSON-звіту"
    )

    args = parser.parse_args()
    success = run_audit(
        map_file=args.map,
        flash_limit=args.flash_max,
        ram_limit=args.ram_max,
        banned_keywords=args.ban,
        json_output_path=args.json
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

## Інтеграція в пайплайн GitHub Actions

Нижче наведено закінчений workflow-файл `.github/workflows/firmware_ci.yml`, який після кроку компіляції викликає скрипт `map_audit.py`, формує артефакти звіту та автоматично публікує гарно відформатований підсумок (*GitHub Step Summary*) прямо на сторінці пулреквесту:

```yaml
name: Embedded Firmware CI & Memory Audit

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-and-verify:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Setup Arm GNU Toolchain & Build Tools
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y --no-install-recommends \
            gcc-arm-none-eabi \
            ninja-build \
            cmake \
            python3

      - name: Configure CMake Project
        run: |
          cmake -B build -G Ninja \
            -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake \
            -DCMAKE_BUILD_TYPE=MinSizeRel

      - name: Compile Firmware & Link
        run: |
          cmake --build build --target firmware.elf

      - name: Execute Memory Map Audit Gate
        run: |
          python3 scripts/map_audit.py \
            --map build/firmware.map \
            --flash-max 90.0 \
            --ram-max 80.0 \
            --ban malloc free __cxa_throw _dtoa_r __udivmoddi4 \
            --json build/memory_report.json

      - name: Publish Markdown Summary to Job Summary
        if: always()
        run: |
          if [ -f build/memory_report.json ]; then
            python3 -c "
          import json
          with open('build/memory_report.json') as f:
              data = json.load(f)
          print('### 📊 Звіт використання пам\'яті прошивки')
          print('| Регіон | Початок | Зайнято (Б) | Ліміт (Б) | Використання |')
          print('| :--- | :--- | :--- | :--- | :--- |')
          for name, r in data['regions'].items():
              print(f'| **{name}** | {r[\"origin\"]} | {r[\"used_bytes\"]} | {r[\"length_bytes\"]} | {r[\"percentage\"]}% |')
          " >> $GITHUB_STEP_SUMMARY
          fi

      - name: Upload Linker Map Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: firmware-build-artifacts
          path: |
            build/*.elf
            build/*.map
            build/*.json
```

## Інтеграція в конвеєр GitLab CI

Для інфраструктури GitLab CI контроль пам'яті налаштовується у файлі `.gitlab-ci.yml`. Завдяки підтримці звітів про метрики (*metrics reports*), GitLab може порівнювати розміри секцій між цільовою гілкою та гілкою мердж-реквесту:

```yaml
stages:
  - build
  - audit

compile_firmware:
  stage: build
  image: alpine:latest
  before_script:
    - apk add --no-cache cmake ninja gcc-arm-none-eabi python3
  script:
    - cmake -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/arm.cmake -DCMAKE_BUILD_TYPE=MinSizeRel
    - cmake --build build
  artifacts:
    paths:
      - build/firmware.elf
      - build/firmware.map
    expire_in: 1 week

memory_audit:
  stage: audit
  image: python:3.11-alpine
  script:
    - python3 scripts/map_audit.py --map build/firmware.map --flash-max 88.0 --ram-max 75.0 --json report.json
  dependencies:
    - compile_firmware
```

## Специфіка багаторегіональних карт пам'яті (CCMRAM, QSPI Flash)

Сучасні мікроконтролери часто мають неоднорідну пам'ять: швидкісну пам'ять ядра CCMRAM (*Core Coupled Memory*) або ITCM/DTCM, основну SRAM та зовнішню пам'ять програм (наприклад, Flash на шині QSPI або OctoSPI з підтримкою прямого виконання коду XIP).

У таких системах скрипт аудиту вирішує важливу проблему: стандартний розрахунок утиліти `size` зводить усю пам'ять до єдиного числа `data + bss`, не розрізняючи, куди саме потрапив буфер — у внутрішню швидку SRAM чи у виділений блок CCMRAM. Завдяки парсингу розділу `Memory Configuration` та прив'язці кожної секції до абсолютних адрес регіонів, скрипт `map_audit.py` автоматично розраховує окремий відсоток заповнення для кожного апаратного блоку:
- Якщо буфер обробки звуку розміщено директивою `__attribute__((section(".ccmram")))`, його байти зараховуються до регіону `CCMRAM`, не спотворюючи ліміт основної оперативної пам'яті `RAM`.
- Якщо важкі графічні шрифти винесено в зовнішню пам'ять `EXT_FLASH` за адресою `0x90000000`, їхній обсяг контролюється окремим лімітом зовнішнього чипа, не викликаючи помилкового переповнення внутрішнього Flash-регіону мікроконтролера.

## Відстеження дельти розміру (Diff Tracking) та розслідування інцидентів

Окрім перевірки абсолютних порогів, ключовою практикою промислової розробки є контроль відносної зміни розміру між поточною збіркою та базовою гілкою `main`. Якщо пулреквест додає лише 50 рядків бізнес-логіки, але збільшує Flash на 12 кілобайтів, скрипт сигналізує про аномалію.

Коли CI відхиляє збірку через перевищення бюджету, інженер виконує розслідування за згенерованим звітом:
1. **Перегляд розділу `[1] Апаратні регіони`**: визначає, яка саме пам'ять вичерпана (енергонезалежна Flash чи оперативна SRAM).
2. **Аналіз таблиці `[2] Топ-10 найбільших функцій`**: виявляє несподіваних лідерів за розміром серед щойно скомпільованих об'єктів.
3. **Перевірка блоку `[3] Заборонені символи`**: показує точне ім'я функції та об'єктний файл, який порушив контракт (наприклад, випадково підтягнув `malloc` через виклик стандартного потоку виводу або створив масив без кваліфікатора `const`).

Впровадження автоматизованого аудиту Map-файлу в CI усуває «людський фактор», гарантує стабільність релізів та захищає команду від несподіваних апаратних збоїв переповнення Flash і SRAM.
