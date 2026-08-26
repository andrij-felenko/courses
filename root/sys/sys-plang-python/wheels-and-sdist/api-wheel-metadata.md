# 📋 Специфікація метаданих wheel: WHEEL, METADATA та RECORD

Службовий каталог `.dist-info` є серцевиною стандартизованого постачання пакетів у Python. Він формується під час упаковування архіву `wheel` і без змін переноситься у каталог `site-packages` цільового середовища під час інсталяції. Структура каталогу та формат файлів суворо регламентовані специфікаціями PEP 427, PEP 566, PEP 610, PEP 627, PEP 643 та PEP 685.

Назва каталогу формується шляхом поєднання канонічної назви дистрибутива та його версії за шаблоном `{distribution}-{version}.dist-info`. Назва дистрибутива та версія проходять процедуру нормалізації (символи підкреслення, крапки та великі літери зводяться до дефісів у нижньому регістрі згідно з PEP 503).

```
{distribution}-{version}.dist-info/
├── WHEEL              # Параметри бінарного контейнера wheel (PEP 427)
├── METADATA           # Паспорт пакета: назва, версія, залежності (Core Metadata)
├── RECORD             # Маніфест цілісності: шляхи, SHA-256 хеші та розміри файлів
├── entry_points.txt   # Декларація консольних команд і плагінів
├── INSTALLER          # Назва інструменту, що виконав установку (pip, uv, flit)
├── REQUESTED          # Маркер явного запиту користувачем (якщо встановлено не як залежність)
├── direct_url.json    # Інформація про джерело (VCS URL, локальний шлях за PEP 610)
└── licenses/          # Ліцензійні угоди та авторські права (PEP 639)
```

## 1. Специфікація файлу WHEEL

Файл `WHEEL` зберігає конфігураційні метадані самого архіву як двійкового контейнера. Синтаксис файлу відповідає поштовому формату заголовків RFC 822: пари «ключ: значення», розділені двокрапкою, де кожен заголовок розташовано на окремому рядку.

Основні поля специфікації PEP 427:

| Поле | Обов'язковість | Формат і призначення | Приклад значення |
|---|---|---|---|
| `Wheel-Version` | Обов'язкове | Версія специфікації формату wheel (наразі `1.0`) | `1.0` |
| `Generator` | Обов'язкове | Назва та версія інструменту, що зібрав архів | `hatchling 1.22.0` |
| `Root-Is-Purelib` | Обов'язкове | Булевий прапорець (`true` або `false`), що вказує каталог розпакування | `false` |
| `Tag` | Обов'язкове (1+) | Трійка тегів сумісності `{python}-{abi}-{platform}`. Допускається множинне оголошення | `cp312-cp312-manylinux_2_28_x86_64` |
| `Build` | Опційне | Номер або мітка збірки для розрізнення однакових версій релізу | `1` |

Семантика прапорця `Root-Is-Purelib` визначає системну поведінку інсталятора:
- Якщо значення дорівнює `true`, вміст кореня архіву вважається чистим кодом мовою Python і розпаковується безпосередньо у загальний каталог `purelib` (`site-packages`).
- Якщо значення дорівнює `false`, архів містить двійкові скомпільовані модулі під конкретну архітектуру. Інсталятор розгортає вміст у платформозалежний каталог `platlib`.

Колеса можуть бути **мультитеговими** (Multi-tag Wheels): якщо один і той самий скомпільований файл або архів чистого Python сумісний з кількома інтерпретаторами чи версіями glibc, файл `WHEEL` містить кілька послідовних рядків `Tag`:

```
Wheel-Version: 1.0
Generator: scikit-build-core 0.9.3
Root-Is-Purelib: false
Tag: cp312-cp312-manylinux_2_28_x86_64
Tag: cp312-cp312-musllinux_1_2_x86_64
```

## 2. Специфікація файлу METADATA та стандарти Core Metadata

Файл `METADATA` містить декларативний опис бібліотеки відповідно до стандарту Core Metadata Specification.

Еволюція специфікації відбиває поступове посилення вимог до детермінованості метаданих:
- **Metadata 1.2 (PEP 345):** запроваджено маркери оточення (Environment Markers) для умовного встановлення залежностей.
- **Metadata 2.1 (PEP 566):** додано підтримку формату опису `Description-Content-Type` (зокрема Markdown замість суворого reStructuredText).
- **Metadata 2.2 (PEP 643):** додано поле `Dynamic`. Раніше збирачі могли довільно змінювати поля метаданих під час виконання, що змушувало резолвер залежностей викачувати весь вихідний код. Поле `Dynamic` явно декларує, які саме поля обчислюються під час збирання, дозволяючи кешувати решту метаданих як незмінні константи.
- **Metadata 2.3 (PEP 685):** нормалізація імен додаткових наборів залежностей (Extras).
- **PEP 658 (Direct Metadata Access):** індекси пакетів (PyPI) отримали можливість віддавати окремий файл `.dist-info/METADATA` без необхідності для клієнта викачувати гігабайтні бінарні архіви коліс для побудови дерева залежностей.

Ключові директиви та їхнє призначення:

| Директива | Кардинальність | Опис поля |
|---|---|---|
| `Metadata-Version` | 1 | Версія формату метаданих (`2.1`, `2.2`, `2.3`) |
| `Name` | 1 | Канонічна назва дистрибутива |
| `Version` | 1 | Версія за стандартом PEP 440 (наприклад, `1.4.2.dev0`) |
| `Summary` | 0..1 | Короткий однорядковий опис призначення бібліотеки |
| `Requires-Python` | 0..1 | Специфікатор підтримуваних версій інтерпретатора (наприклад, `>=3.10,<3.14`) |
| `Requires-Dist` | 0..N | Залежність пакета з необов'язковими маркерами оточення PEP 508 |
| `Provides-Extra` | 0..N | Назва опційного набору додаткових залежностей (екстра) |
| `Description-Content-Type` | 0..1 | Формат основного опису (`text/markdown`, `text/x-rst`, `text/plain`) |
| `Dynamic` | 0..N | Перелік полів, які розраховуються динамічно бекендом під час збирання |
| `License-Expression` | 0..1 | SPDX-вираз ліцензії за стандартом PEP 639 (наприклад, `MIT OR Apache-2.0`) |

Зразок заповненого маніфесту `METADATA`:

```
Metadata-Version: 2.3
Name: fast-engine
Version: 0.4.2
Summary: High performance native data processing engine
Requires-Python: >=3.10
Requires-Dist: numpy>=1.24.0
Requires-Dist: pyarrow>=14.0.0; extra == "arrow"
Requires-Dist: uvloop>=0.19.0; (sys_platform != "win32") and (extra == "async")
Provides-Extra: arrow
Provides-Extra: async
Description-Content-Type: text/markdown

# Fast Engine
Високопродуктивний рушій обробки потокових даних із вбудованим C++ бекендом.
```

## 3. Додаткові службові файли: direct_url.json та .data каталог

Каталог `.dist-info` підтримує фіксацію походження дистрибутива та розгортання системних ресурсів:

### Фіксація джерела за стандартом PEP 610 (direct_url.json)
Якщо пакет було встановлено не з основного індексу PyPI, а з системи контролю версій Git або локального каталогу у режимі розробника (`pip install -e .`), у каталозі `.dist-info` створюється файл `direct_url.json`. Він містить URL-адресу репозиторію, точний хеш коміту (`commit_id`) та булевий прапорець `editable`:

```json
{
  "url": "https://github.com/org/fast-engine.git",
  "vcs_info": {
    "vcs": "git",
    "requested_revision": "main",
    "commit_id": "8f3b2a9c1e7d4f506821bc34"
  }
}
```

### Розподіл ресурсів через каталог .data
Якщо пакет містить C-заголовки для компіляції сторонніх модулів або виконувані утиліти, вони упаковуються у підкаталоги `{distribution}-{version}.data/`:
- `headers/`: C/C++ файли `.h`, які копіюються в системний каталог `include/` інтерпретатора.
- `scripts/`: виконувані скрипти, які переносяться в `bin/` із автоматичним оновленням рядка Shebang на `sys.executable`.
- `data/`: конфігурації та ресурси, що копіюються в корінь середовища `sys.prefix`.

## 4. Точки входу: entry_points.txt

Файл `entry_points.txt` реалізує стандартизований механізм реєстрації плагінів та консольних утиліт у форматі конфігураційного файлу INI.

```ini
[console_scripts]
fast-engine-cli = fast_engine.cli:main_entry
fast-admin = fast_engine.admin:run

[gui_scripts]
fast-ui = fast_engine.gui:start_window

[pytest11]
fast_plugin = fast_engine.pytest_plugin
```

Коли менеджер `pip` розпаковує wheel, що містить секцію `[console_scripts]`, він генерує у каталозі `bin/` скомпільований бінарний запускник або виконуваний Python-скрипт, який імпортує функцію `main_entry` із зазначеного модуля та передає їй керування. Під час виконання застосунок може динамічно виявляти зареєстровані точки розширення через стандартний модуль `importlib.metadata.entry_points(group="pytest11")`.

## 5. Специфікація маніфесту RECORD

Файл `RECORD` є криптографічно захищеним реєстром файлів, що гарантує цілісність інсталяції та уможливлює чисте видалення пакета.

Формат файлу — це таблиця значень у форматі CSV (RFC 4180), де кожен рядок описує рівно один фізичний файл у складі дистрибутива:

```
{шлях_відносно_кореня},{алгоритм}={хеш_base64url},{розмір_у_байтах}
```

Вимоги до формування записів маніфесту:
1. **Алгоритм хешування:** стандартом закріплено криптографічну хеш-функцію `sha256`. Використання слабких або застарілих алгоритмів (`md5`, `sha1`) заборонено.
2. **Формат кодування дайджесту:** сирий 32-байтовий бінарний дайд SHA-256 кодується в URL-безпечний варіант Base64 (RFC 4648 §5). У цьому алфавіті символи `+` та `/` замінюються на `-` та `_` відповідно, а кінцеві символи вирівнювання `=` відкидаються. Це гарантує, що рядок хешу не містить спеціальних символів, які можуть пошкодити розбір CSV.
3. **Запис для самого файлу RECORD:** файл `RECORD` не може містити власний хеш під час формування маніфесту. Тому рядок, що посилається на `...dist-info/RECORD`, обов'язково залишає поля хешу та розміру порожніми (`{шлях},,`).

Приклад реального вмісту файлу `RECORD`:

```
fast_engine/__init__.py,sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU,128
fast_engine/core.py,sha256=M8o9K4_L3n2P1q7R5s6T4u8V9w0X1y2Z3a4B5c6D7e8,1450
fast_engine/_core.cpython-312-x86_64-linux-gnu.so,sha256=p4K38jL9aW4y_kI3dM6zX1v0B9Q2R8tY5uP7sE1aG3o,98304
fast_engine-0.4.2.dist-info/METADATA,sha256=N0p1Q2r3S4t5U6v7W8x9Y0z1A2b3C4d5E6f7G8h9I0j,1380
fast_engine-0.4.2.dist-info/WHEEL,sha256=a8F3_k9L1m2N3o4P5q6R7s8T9u0V1w2X3y4Z5a6B7c8,142
fast_engine-0.4.2.dist-info/RECORD,,
```

## 6. Алгоритм валідації та генерації маніфесту RECORD

Під час встановлення пакета менеджер `pip` зчитує файл `RECORD`, розраховує фактичні контрольні суми витягнутих на диск файлів і звіряє їх із записами в маніфесті. Якщо контрольна сума хоча б одного файлу не збігається, встановлення переривається з помилкою пошкодження архіву.

Наведений нижче модуль мовою Python демонструє еталонну реалізацію генерації та валідації маніфесту цілісності:

```py
import base64
import csv
import hashlib
from pathlib import Path


def calculate_sha256_base64url(data: bytes) -> str:
    """Обчислити SHA-256 дайджест у форматі base64url без вирівнювання '='."""
    digest = hashlib.sha256(data).digest()
    # RFC 4648 urlsafe base64 з видаленням кінцевих '='
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def generate_record_for_wheel(root_dir: Path, dist_info_dirname: str) -> None:
    """Згенерувати валідний файл RECORD для вмісту каталогу колеса."""
    record_rel_path = f"{dist_info_dirname}/RECORD"
    rows: list[tuple[str, str, str | int]] = []

    # Обхід усіх файлів у дереві розпакованого пакета
    for file_path in sorted(root_dir.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(root_dir).as_posix()
            
            # Файл RECORD не фіксує власний хеш
            if rel_path == record_rel_path:
                continue

            file_bytes = file_path.read_bytes()
            hash_str = calculate_sha256_base64url(file_bytes)
            rows.append((rel_path, f"sha256={hash_str}", len(file_bytes)))

    # Додавання обов'язкового порожнього запису для самого RECORD
    rows.append((record_rel_path, "", ""))

    output_record_path = root_dir / dist_info_dirname / "RECORD"
    with open(output_record_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def verify_installed_record(root_dir: Path, dist_info_dirname: str) -> bool:
    """Перевірити цілісність встановленого пакета за даними файлу RECORD."""
    record_path = root_dir / dist_info_dirname / "RECORD"
    if not record_path.exists():
        raise FileNotFoundError(f"Файл маніфесту не знайдено: {record_path}")

    with open(record_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            rel_path, expected_hash, expected_size = row
            target_file = root_dir / rel_path

            # Пропуск запису самого RECORD
            if not expected_hash:
                continue

            if not target_file.exists():
                print(f"Помилка: відсутній файл {rel_path}")
                return False

            data = target_file.read_bytes()
            actual_size = str(len(data))
            algo, hash_val = expected_hash.split("=", 1)

            if algo != "sha256":
                print(f"Помилка: невідомий алгоритм хешування {algo}")
                return False

            actual_hash = calculate_sha256_base64url(data)
            if actual_hash != hash_val or actual_size != expected_size:
                print(f"Помилка цілісності: файл {rel_path} змінено на диску!")
                return False

    return True
```
