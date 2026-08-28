# ⚙️ Трасувальник .pth: хто додав цей шлях і що виконалося до вашого коду

Список `sys.path` — це плаский масив рядків без жодного сліду походження: дивлячись на каталог `/home/dev/legacy/src` на позиції 9, ви не дізнаєтеся, чи його вписав editable-встановлений пакет, чи забутий три роки тому `easy-install.pth`, чи рядок `import` із чужого файла. Нижче зібрано робочий інструмент `pth_trace.py`, який повторює алгоритм `site.addsitedir()` крок у крок і повертає кожному елементу `sys.path` його автора — файл і номер рядка, — а також показує, який саме код виконався до першої інструкції вашої програми. Друга частина — як безпечно написати власний стартовий гачок на `.pth`, не поклавши кожен інтерпретатор у системі.

## 1. Задача: список без авторства

Типовий збій виглядає так. Розробник ставить пакет у режимі розробки, потім перейменовує теку проєкту, потім ставить його ще раз — і в середовищі лишається два `.pth`, один з яких указує в нікуди, а другий тягне стару копію коду. Імпорт формально працює, тести зелені, але модуль підвантажується не з того дерева, яке редагують. Або інший випадок: у `sys.path` на позиції нуль з'являється каталог, якого туди ніхто не додавав, — бо рядок `import` у чужому `.pth` викликав `sys.path.insert(0, ...)`.

Стандартні засоби відповідають на це погано. Прапорець `-v` вивалює сотні рядків про кожну спробу відкрити файл, і `.pth` тонуть у цьому потоці. `site.getsitepackages()` показує теки, але не їхній вміст. Отже, інструменту треба відповісти на два різні питання:

1. **Хто додав цей каталог?** Для кожного елемента `sys.path` — назвати джерело: точка входу, `PYTHONPATH`, стандартна бібліотека, сам каталог `site-packages` чи конкретний рядок конкретного `.pth`.
2. **Що виконалося?** Перелічити всі рядки `import`, які інтерпретатор уже прогнав через `exec()` під час старту, — разом із файлом, звідки вони прийшли.

## 2. Ідея: повторити алгоритм, а не вгадувати його

Спокуса — прочитати всі `.pth` і просто зібрати з них шляхи. Це дає неправильну відповідь, бо `site` не додає все підряд. Він працює так (`Lib/site.py`, функції `addsitedir` і `addpackage`), і саме цю послідовність треба відтворити дослівно:

- у теці беруться лише імена, що закінчуються на `.pth`, і сортуються звичайним порівнянням рядків — тобто за кодами символів, а не за алфавітом мови;
- **прихований файл пропускається цілком** — на macOS/BSD за прапорцем `UF_HIDDEN`, на Windows за атрибутом `FILE_ATTRIBUTE_HIDDEN`;
- вміст читається як байти й декодується спершу як UTF-8, і лише при невдачі — кодуванням файлової системи;
- рядок, що починається з `#`, і порожній рядок пропускаються;
- рядок, що починається з `import ` або `import\t`, іде в `exec()`;
- будь-який інший рядок трактується як шлях: він склеюється з текою самого `.pth`, зводиться до абсолютного через `abspath()` і нормалізується `normcase()`; додається в **кінець** `sys.path` — і лише якщо його ще немає в множині `known_paths` **і** каталог справді існує на диску.

Два наслідки з цього списку варто засвоїти окремо, бо саме на них тримається трасувальник. По-перше, `.pth` **дописує в хвіст**, а не на початок: перекрити встановлений пакет через `.pth` неможливо в принципі, хоч скільки разів переставляй рядки місцями. По-друге, перевірка `known_paths` означає, що другий файл, який називає той самий каталог, не робить нічого — і винним у поведінці системи виглядатиме він, хоча реальний автор запису лежить вище за сортуванням.

Є й межа, яку інструмент не може перестрибнути чесно: ми запускаємося вже після `site`, коли `sys.path` сформований. Відновити початкову множину `known_paths` неможливо. Але її можна вирахувати з форми результату: оскільки `.pth` пише виключно в хвіст, усе, що стоїть у `sys.path` **до першого каталогу `site-packages`**, гарантовано потрапило туди раніше — це точка входу, `PYTHONPATH` і стандартна бібліотека. Цим і засіваємо множину відомого.

## 3. Робочий код

Інструмент — один файл без сторонніх залежностей. Він не виконує жодного рядка з чужих `.pth`: рядки `import` він лише показує як текст, бо виконав їх уже сам інтерпретатор, і другий прогін тих самих гачків зіпсував би середовище, яке ми діагностуємо.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pth_trace.py — повертає кожному елементу sys.path його автора."""

from __future__ import annotations

import io
import os
import site
import stat
import sys
from dataclasses import dataclass


def makepath(*parts: str) -> tuple[str, str]:
    """Точний відповідник site.makepath: абсолютний шлях і його ключ порівняння."""
    joined = os.path.abspath(os.path.join(*parts))
    return joined, os.path.normcase(joined)


@dataclass(frozen=True)
class PthLine:
    file: str
    lineno: int
    raw: str
    kind: str                    # "path" | "exec" | "comment" | "blank" | "hidden"
    target: str | None = None    # розрахований каталог для kind == "path"
    note: str = ""               # чому рядок не спрацював

    def where(self) -> str:
        return f"{os.path.basename(self.file)}:{self.lineno}"


class PthReplay:
    """Повторює site.addsitedir() без побічних дій."""

    def __init__(self, sitedirs: list[str]) -> None:
        self.sitedirs = sitedirs
        self.lines: list[PthLine] = []
        self.owner: dict[str, PthLine] = {}   # ключ normcase → рядок-автор
        self.known: set[str] = set()

    def run(self) -> "PthReplay":
        cases = {makepath(d)[1] for d in self.sitedirs}
        for entry in sys.path:                 # усе до першого site-packages
            if entry and makepath(entry)[1] in cases:
                break
            if entry:
                self.known.add(makepath(entry)[1])
        for sitedir in self.sitedirs:
            self._scan_dir(sitedir)
        return self

    def _scan_dir(self, sitedir: str) -> None:
        base, basecase = makepath(sitedir)
        if not os.path.isdir(base):
            return
        self.known.add(basecase)               # site додає саму теку перед скануванням
        names = sorted(n for n in os.listdir(base) if n.endswith(".pth"))
        for name in names:
            self._scan_file(base, name)

    def _scan_file(self, base: str, name: str) -> None:
        full = os.path.join(base, name)
        try:
            st = os.lstat(full)
        except OSError:
            return
        hidden = ((getattr(st, "st_flags", 0) & getattr(stat, "UF_HIDDEN", 0)) or
                  (getattr(st, "st_file_attributes", 0)
                   & getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 0)))
        if hidden:
            self.lines.append(PthLine(full, 0, "", "hidden",
                                      note="прихований файл — site його не читає"))
            return

        with io.open_code(full) as fh:
            blob = fh.read()
        try:
            text = blob.decode()
        except UnicodeDecodeError:
            text = blob.decode(sys.getfilesystemencoding())

        for n, raw in enumerate(text.splitlines(), 1):
            self.lines.append(self._classify(base, full, n, raw))

    def _classify(self, base: str, full: str, n: int, raw: str) -> PthLine:
        if raw.startswith("#"):
            return PthLine(full, n, raw, "comment")
        if not raw.strip():
            return PthLine(full, n, raw, "blank")
        if raw.startswith(("import ", "import\t")):
            return PthLine(full, n, raw, "exec",
                           note="виконано під час старту процесу")

        target, case = makepath(base, raw.rstrip())
        if case in self.known:
            return PthLine(full, n, raw, "path", target,
                           "дублікат — каталог уже був у списку")
        if not os.path.exists(target):
            return PthLine(full, n, raw, "path", target,
                           "каталогу нема на диску — рядок мовчки пропущено")

        line = PthLine(full, n, raw, "path", target, "додано в кінець sys.path")
        self.known.add(case)
        self.owner[case] = line
        return line
```

Друга половина — звіт. Він проходить справжній `sys.path` і для кожного запису шукає автора: спершу серед очевидних джерел, потім у мапі `owner`, зібраній повтором алгоритму.

```python
def attribute(replay: PthReplay) -> list[tuple[int, str, str]]:
    """Кожному елементу sys.path — рядок пояснення, звідки він узявся."""
    env = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    env_cases = {makepath(p)[1] for p in env}
    site_cases = {makepath(d)[1] for d in replay.sitedirs}
    prefixes = tuple(makepath(p)[1] for p in (sys.prefix, sys.base_prefix))

    rows: list[tuple[int, str, str]] = []
    for i, entry in enumerate(sys.path):
        if entry == "":
            rows.append((i, entry, "порожній рядок — поточний каталог процесу"))
            continue
        case = makepath(entry)[1]
        if case in site_cases:
            source = "каталог site-packages (додав site.addsitedir)"
        elif case in env_cases:
            source = "змінна оточення PYTHONPATH"
        elif case in replay.owner:
            line = replay.owner[case]
            source = f".pth → {line.where()}  «{line.raw.strip()}»"
        elif case.startswith(prefixes):
            source = "стандартна бібліотека (розрахунок префікса)"
        elif i == 0:
            source = "точка входу: каталог скрипту або cwd"
        else:
            source = "НЕВІДОМО — мутація під час виконання або рядок import у .pth"
        rows.append((i, entry, source))
    return rows


def main() -> int:
    sitedirs = list(site.getsitepackages())
    if site.ENABLE_USER_SITE:
        sitedirs.append(site.getusersitepackages())
    replay = PthReplay(sitedirs).run()

    print("=== sys.path з авторством ===")
    for i, entry, source in attribute(replay):
        print(f"[{i:2d}] {entry or '(порожньо)'}\n     ↳ {source}")

    execs = [ln for ln in replay.lines if ln.kind == "exec"]
    if execs:
        print("\n=== код, що виконався до вашої програми ===")
        for ln in execs:
            print(f"  {ln.where():40s} {ln.raw.strip()}")

    dead = [ln for ln in replay.lines
            if ln.kind == "path" and "нема на диску" in ln.note]
    if dead:
        print("\n=== мертві рядки (каталог зник) ===")
        for ln in dead:
            print(f"  {ln.where():40s} → {ln.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Запуск `python -m pth_trace` у здоровому середовищі дає нудний стовпчик пояснень; у зіпсованому одразу видно і мертві записи, і чужий гачок, і рядок `НЕВІДОМО`, який означає рівно одне: цей каталог у список поклав виконаний код, а не декларація.

## 4. Власний гачок: як зробити його й не покласти систему

Формат `.pth` дозволяє лише **один логічний рядок**: жодних відступів, блоків, `def` чи `try` у самому файлі. Тому єдиний придатний спосіб — рядок, який імпортує звичайний модуль поруч, а вся логіка живе в тому модулі:

Файл `zz_bootstrap.pth` у `site-packages` (одна стрічка):

```
import zz_bootstrap
```

Файл `zz_bootstrap.py` там-таки:

```python
"""Стартовий гачок: вмикається на кожен запуск інтерпретатора. Має бути дешевий і німий."""

import os
import sys


def _configure() -> None:
    if os.environ.get("ZZ_BOOTSTRAP_OFF"):      # аварійний вимикач
        return
    # Нічого важкого тут не імпортуємо: цей код платить своєю ціною
    # за КОЖЕН запуск python у системі, включно з pip і мовним сервером IDE.
    sys.stdout.reconfigure(errors="backslashreplace")


try:
    _configure()
except Exception:                                # гачок не має права зривати старт
    import traceback
    traceback.print_exc()
```

Три обов'язкові властивості такого модуля: **вимикач через змінну оточення** (щоб зняти гачок, не маючи прав на запис у `site-packages`), **власний `try/except` навколо всього** і **порожній старт** — жодних важких імпортів на рівні модуля.

Префікс `zz_` в імені — не забобон: файли обробляються в порядку сортування рядків, і гачок, який хоче бачити вже наповнений `sys.path`, мусить іти після інших. Пам'ятайте лише, що в порядку кодів символів символ підкреслення стоїть **після** великих літер і **перед** малими: файл `__editable__foo.pth` обробиться пізніше за `Foo.pth`, але раніше за `bar.pth`.

## 5. Пастки, через які це зазвичай і ламається

**Рядок помер — решта файла теж.** Якщо під час обробки рядка виникає виняток, `site` друкує в `stderr` повідомлення «Error processing line N of ...» і **припиняє читати цей файл**, дописуючи «Remainder of file ignored». Решта `.pth` у теці обробиться нормально. Тобто одна зламана стрічка тихо вимикає всі наступні стрічки того самого файла — а якщо `stderr` процесу відведено в нікуди (демон, служба, планувальник), ви не побачите взагалі нічого.

**Імена, створені рядком `import`, ніде не лишаються.** `exec()` виконується в просторі імен функції `addpackage` модуля `site`. Присвоїти щось «глобально» цим рядком не можна: він мусить діяти **побічним ефектом** — зареєструвати шукача в `sys.meta_path`, змінити `sys.path`, підмінити атрибут чужого модуля. Саме тому editable-встановлення за PEP 660 виглядають як `import _editable_..._finder; _editable_..._finder.install()`, а не як присвоєння.

**Відносний шлях рахується від теки самого `.pth`, не від робочого каталогу.** А от абсолютний шлях, який туди вписав менеджер пакетів, не переживе перенесення проєкту: перейменували теку — і editable-встановлення вказує в порожнечу, мовчки, бо неіснуючий каталог просто пропускається без попередження.

**Ціна старту.** Кожен рядок `import` виконується при **кожному** запуску інтерпретатора: `python -c "print(1)"`, виклик `pip`, підказки мовного сервера в редакторі. Гачок, що тягне важку бібліотеку, додає свої десятки мілісекунд усьому, що є на машині. Міряти це просто: `python -X importtime -c pass` покаже винуватця поіменно.

**`-S` і `-I` вимикають усе це цілком.** Класичний рапорт «у мене працює, а в systemd-юніті ні» майже завжди означає, що служба стартує в ізольованому режимі, де `site` не запускається, а отже, немає ні `site-packages`, ні `.pth`, ні гачків.

**Права на запис у `site-packages` дорівнюють виконанню коду.** Файл `.pth` не треба нікуди імпортувати й нічим не треба викликати — досить покласти його поруч. Це стосується й користувацької теки `~/.local/lib/pythonX.Y/site-packages`, куди пише звичайний `pip install --user` без жодних адміністраторських прав.
