# ⚙️ Автономний виконуваний пакунок zipapp та C/C++ завантажувач

Пакування кодової бази у виконуваний автономний архів zipapp (PEP 441) дозволяє поширювати комплексні утиліти Python у вигляді єдиного переносимого бінарного файлу з єдиною точкою входу `__main__.py`. Нижче реалізовано повний виробничий цикл створення такого пакунка: структуру вихідного проєкту, автоматизований збирач стисненого архіву з Unix-шебангом засобами Python, створення системного завантажувача мовами C та C++ з використанням сучасного CPython C API, а також аналіз низькорівневого стану простору імен `__main__` і діагностику внутрішньої структури файлу.

## 1. Архітектура проєкту та структура каталогу

Для демонстрації повного циклу розробки створимо мікросервіс моніторингу системних ресурсів. Проєкт організовано у вигляді пакета з чітким розділенням збору метрик, форматування виводу та точки входу.

Структура вихідних файлів проєкту перед початком збирання:

```
system_monitor/
├── monitor/
│   ├── __init__.py
│   ├── collector.py
│   └── formatter.py
└── __main__.py
```

Файл `monitor/__init__.py` ініціалізує пакет і фіксує його версію:
```python
"""Пакет збору та форматування системних метрик."""

__version__ = "1.0.0"
```

Файл `monitor/collector.py` реалізує збір базової інформації про операційне середовище процесу:
```python
import os
import platform
import sys


def collect_metrics() -> dict[str, str | int]:
    """Збирає базову інформацію про середовище виконання."""
    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    return {
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "pid": os.getpid(),
        "load_1m": load_avg[0],
        "load_5m": load_avg[1],
        "load_15m": load_avg[2],
    }
```

Файл `monitor/formatter.py` форматує зібрані дані у зручний для читання текстовий звіт:
```python
def format_text(metrics: dict[str, str | int]) -> str:
    """Перетворює словник метрик у читабельний текстовий звіт."""
    lines = [
        "=== ЗВІТ СИСТЕМНОГО МОНІТОРИНГУ ===",
        f"Платформа:       {metrics['platform']}",
        f"Версія Python:   {metrics['python_version']}",
        f"PID процесу:     {metrics['pid']}",
        f"Навантаження:    1хв={metrics['load_1m']:.2f}, 5хв={metrics['load_5m']:.2f}, 15хв={metrics['load_15m']:.2f}",
        "==================================",
    ]
    return "\n".join(lines)
```

Головна точка входу `__main__.py` розташована в корені каталогу застосунку. Вона пов'язує компоненти в єдину консольну програму і повертає цілочисельний статус завершення:
```python
import sys
from monitor.collector import collect_metrics
from monitor.formatter import format_text


def main() -> int:
    """Точка входу автономного пакунка."""
    try:
        metrics = collect_metrics()
        output = format_text(metrics)
        print(output)
        return 0
    except Exception as err:
        sys.stderr.write(f"Помилка виконання монітора: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## 2. Автоматизований збирач zipapp-пакета на Python

Для створення переносимого автономного файлу напишемо скрипт автоматизації `builder.py`. Скрипт перевіряє наявність файлу `__main__.py`, формує стиснений ZIP-архів із компресією `DEFLATE`, додає стандартний виконуваний шебанг `#!/usr/bin/env python3` та виставляє права доступу POSIX `0o755` (`rwxr-xr-x`).

Зверніть увагу на алгоритм обробки шляхів: функція `zipapp.create_archive()` зчитує всі вкладені модулі, створює заголовок шебангу з переносом рядка `\n` і записує бінарні структури ZIP безпосередньо після нього.

```python
#!/usr/bin/env python3
import os
import stat
import zipapp
from pathlib import Path


def build_standalone_zipapp(
    source_dir: str | Path,
    output_file: str | Path,
    shebang: str = "/usr/bin/env python3",
) -> None:
    """Збирає автономний zipapp-архів із каталогу source_dir."""
    src = Path(source_dir).resolve()
    out = Path(output_file).resolve()

    if not (src / "__main__.py").exists():
        raise FileNotFoundError(
            f"Каталог {src} не містить обов'язкового файлу точки входу __main__.py"
        )

    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Збирання zipapp: {src} -> {out}...")
    zipapp.create_archive(
        source=src,
        target=out,
        interpreter=shebang,
        main=None,  # Використовувати наявний файл __main__.py у корені каталогу
        compressed=True,
    )

    # Встановлюємо права виконання rwxr-xr-x для систем Unix/Linux/macOS
    current_mode = os.stat(out).st_mode
    os.chmod(out, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Архів створено успішно (розмір: {out.stat().st_size} байтів).")


if __name__ == "__main__":
    build_standalone_zipapp("system_monitor", "bin/sysmon.pyz")
```

Після виконання скрипту утворюється файл `bin/sysmon.pyz`. Користувач у POSIX-терміналі може запустити його безпосередньо як `./bin/sysmon.pyz` або через передачу інтерпретатору `python3 bin/sysmon.pyz`.

## 3. Системний C та C++ завантажувач через CPython C API

Коли автономний пакунок необхідно інтегрувати в нативний C або C++ застосунок (наприклад, графічний рушій, промисловий контролер або системну службу), інтерпретатор ініціалізується вручну, а файл `.pyz` передається в середовище через низькорівневу конфігурацію `PyConfig`.

Процес ініціалізації вимагає точного дотримання послідовності викликів стандарту PEP 587: спершу заповнюється конфігураційна структура, налаштовується прапорець парсингу аргументів `parse_argv = 1`, передається ім'я архіву в поле `config.run_filename`, і лише після цього викликається функція `Py_InitializeFromConfig()`. Завершальний виклик `Py_RunMain()` завантажує `__main__.py` та повертає код виходу програми.

:::tabs
```c
/* runner.c — Системний C-завантажувач для zipapp-пакета */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

int run_zipapp_package(const char* pyz_path, int argc, char* argv[]) {
    PyStatus status;
    PyConfig config;

    /* Ініціалізуємо базову структуру конфігурації CPython */
    PyConfig_InitPythonConfig(&config);
    config.parse_argv = 1;

    /* Встановлюємо ім'я файлу zipapp як цільовий сценарій виконання */
    status = PyConfig_SetBytesString(&config, &config.run_filename, pyz_path);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Помилка встановлення шляху run_filename\n");
        return 1;
    }

    /* Передаємо аргументи командного рядка у середовище Python */
    status = PyConfig_SetBytesArgv(&config, argc, argv);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Помилка встановлення argv у PyConfig\n");
        return 1;
    }

    /* Ініціалізуємо ядро середовища CPython */
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Помилка ініціалізації середовища CPython\n");
        return 1;
    }
    PyConfig_Clear(&config);

    /* Запускаємо модуль __main__ цільового архіву через головну точку входу */
    int exit_code = Py_RunMain();
    return exit_code;
}

int main(int argc, char* argv[]) {
    const char* pyz_file = "bin/sysmon.pyz";
    if (argc > 1) {
        pyz_file = argv[1];
    }

    printf("[C Host] Запуск автономного Python zipapp: %s\n", pyz_file);
    int result = run_zipapp_package(pyz_file, argc, argv);
    printf("[C Host] Виконання завершено з кодом: %d\n", result);
    return result;
}
```
```cpp
// runner.cpp — Сучасний C++20 завантажувач із RAII та керуванням винятками
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <vector>
#include <span>

class PythonRuntime {
public:
    PythonRuntime(std::string_view pyz_path, std::span<char*> args) {
        PyConfig config;
        PyConfig_InitPythonConfig(&config);
        config.parse_argv = 1;

        PyStatus status = PyConfig_SetBytesString(&config, &config.run_filename, pyz_path.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося встановити шлях до zipapp архіву");
        }

        status = PyConfig_SetBytesArgv(&config, static_cast<int>(args.size()), args.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося ініціалізувати аргументи argv");
        }

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);

        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Фатальний збій ініціалізації ядра CPython");
        }
    }

    ~PythonRuntime() {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    PythonRuntime(const PythonRuntime&) = delete;
    PythonRuntime& operator=(const PythonRuntime&) = delete;

    [[nodiscard]] int run() noexcept {
        return Py_RunMain();
    }
};

int main(int argc, char* argv[]) {
    try {
        std::string_view pyz_file = (argc > 1) ? argv[1] : "bin/sysmon.pyz";
        std::span<char*> args(argv, static_cast<size_t>(argc));

        std::cout << "[C++ Host] Ініціалізація CPython для: " << pyz_file << std::endl;
        PythonRuntime runtime(pyz_file, args);
        int exit_code = runtime.run();
        std::cout << "[C++ Host] Код завершення: " << exit_code << std::endl;
        return exit_code;
    } catch (const std::exception& ex) {
        std::cerr << "[C++ Error] " << ex.what() << std::endl;
        return 1;
    }
}
```
:::

## 4. Аналіз внутрішнього стану модуля `__main__` через C API

Після запуску zipapp внутрішній стан модуля `__main__` можна безпосередньо проінспектувати та модифікувати з хост-програми C/C++. Наприклад, отримати доступ до словника модуля та перевірити системні атрибути `__file__`, `__spec__` і `__package__`.

Зверніть увагу: функція `PyModule_GetDict()` повертає запозичене посилання (Borrowed Reference), яке не вимагає зменшення лічильника посилань через `Py_DECREF`. Натомість значення, отримані функціями `PyObject_Str()` або `PyObject_GetAttrString()`, створюють нові об'єкти (New References) і вимагають обов'язкового звільнення пам'яті.

:::tabs
```c
/* inspect_main.c — Інспекція стану __main__ після завантаження */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

void inspect_main_module(void) {
    /* Отримуємо вказівник на завантажений модуль __main__ */
    PyObject* main_mod = PyImport_AddModule("__main__");
    if (!main_mod) {
        PyErr_Print();
        return;
    }

    PyObject* main_dict = PyModule_GetDict(main_mod); /* Запозичене посилання */

    /* Зчитуємо системні атрибути __file__ та __loader__ */
    PyObject* py_file = PyDict_GetItemString(main_dict, "__file__");
    PyObject* py_spec = PyDict_GetItemString(main_dict, "__spec__");

    if (py_file) {
        PyObject* str_repr = PyObject_Str(py_file);
        const char* file_str = PyUnicode_AsUTF8(str_repr);
        printf("[C Debug] __main__.__file__ = %s\n", file_str);
        Py_XDECREF(str_repr);
    }

    if (py_spec && py_spec != Py_None) {
        PyObject* spec_name = PyObject_GetAttrString(py_spec, "name");
        if (spec_name) {
            printf("[C Debug] __main__.__spec__.name = %s\n", PyUnicode_AsUTF8(spec_name));
            Py_DECREF(spec_name);
        }
    }
}
```
```cpp
// inspect_main.cpp — Інспекція стану __main__ мовою C++
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string_view>

void inspect_main_module_cpp() {
    PyObject* main_mod = PyImport_AddModule("__main__");
    if (!main_mod) {
        PyErr_Print();
        return;
    }

    PyObject* main_dict = PyModule_GetDict(main_mod);

    auto print_attr = [main_dict](const char* attr_name) {
        PyObject* val = PyDict_GetItemString(main_dict, attr_name);
        if (val && val != Py_None) {
            PyObject* repr = PyObject_Str(val);
            std::cout << "[C++ Debug] __main__." << attr_name << " = " 
                      << PyUnicode_AsUTF8(repr) << std::endl;
            Py_XDECREF(repr);
        }
    };

    print_attr("__file__");
    print_attr("__package__");
    print_attr("__doc__");
}
```
:::

## 5. Діагностика структури файлу zipapp системними утилітами

Для верифікації правильності сформованого zipapp-файлу використовують стандартні системні інструменти аналізу файлових заголовків у терміналі Linux/macOS:

1. **Перевірка типу файлу через утиліту `file`:**
   ```bash
   $ file bin/sysmon.pyz
   bin/sysmon.pyz: Python script, ASCII text executable, with ZIP prepended
   ```
   Утиліта розпізнає текстовий шебанг на початку файлу і водночас фіксує наявність ZIP-структур.

2. **Інспекція перших байтів файлу (шебанг):**
   ```bash
   $ head -n 1 bin/sysmon.pyz
   #!/usr/bin/env python3
   ```

3. **Перегляд вмісту ZIP-архіву без розпакування:**
   ```bash
   $ unzip -l bin/sysmon.pyz
   Archive:  bin/sysmon.pyz
     Length      Date    Time    Name
   ---------  ---------- -----   ----
         312  2026-08-26 12:00   __main__.py
          68  2026-08-26 12:00   monitor/__init__.py
         480  2026-08-26 12:00   monitor/collector.py
         410  2026-08-26 12:00   monitor/formatter.py
   ---------                     -------
        1270                     4 files
   ```
   Стандартна утиліта `unzip` ігнорує початковий шебанг, оскільки знаходить таблицю файлів з кінця архіву (EOCD).

4. **Діагностика через модуль `zipapp`:**
   ```bash
   $ python3 -m zipapp --info bin/sysmon.pyz
   Interpreter: /usr/bin/env python3
   Main function: (none specified)
   ```

## 6. Підводні камені, системні обмеження та діагностика zipapp

Під час виробничої експлуатації zipapp-пакунків розробники стикаються з трьома критичними архітектурними обмеженнями підсистеми `zipimport`:

### 1. Неможливість прямого завантаження бінарних C-розширень (`.so`, `.pyd`)

Підсистема `zipimport` CPython працює виключно з чистим байткодом (`.pyc`) та вихідними файлами (`.py`). Вона не здатна завантажувати скомпільовані динамічні бібліотеки мови C (`.so` у Linux, `.dylib` у macOS або `.pyd` у Windows).

Причина полягає в архітектурі системних динамічних завантажувачів операційної системи (`ld.so` у Unix або `ntdll.dll` у Windows). Системний виклик `dlopen()` або функція `LoadLibrary()` приймають як аргумент фізичний шлях до файлу у файловій системі або чинний файловий дескриптор. Оскільки файли всередині архіву стиснені і не мають дескриптора файлової системи, ядро ОС не може відобразити їхні секції коду (`.text`, `.rodata`) у віртуальну пам'ять процесу.

Якщо застосунок вимагає використання таких бібліотек, як `numpy`, `cryptography` або `cffi`, застосовують одне з таких рішень:
- Використання інструментів повного пакування (як-от PyInstaller або Nuitka), які видобувають бінарні бібліотеки у тимчасовий каталог (`/tmp/_MEIxxxxxx`) перед викликом `dlopen()`.
- Встановлення C-розширень у спільне системне середовище або віртуальне оточення, залишаючи в `zipapp` лише високорівневу логіку Python.

### 2. Читання статичних ресурсів і конфігурацій

Спроба прочитати вбудований файл конфігурації за допомогою стандартної функції `open(os.path.join(os.path.dirname(__file__), 'config.json'))` завершиться винятком `FileNotFoundError`, оскільки шлях виглядатиме як `/usr/local/bin/sysmon.pyz/monitor/config.json`, що не є реальним каталогом операційної системи.

Сучасний ідіоматичний спосіб роботи з внутрішніми ресурсами — використання модуля `importlib.resources`:

```python
import importlib.resources

def load_embedded_config() -> str:
    """Безпечне читання конфігурації безпосередньо з архіву zipapp."""
    ref = importlib.resources.files("monitor").joinpath("config.json")
    return ref.read_text(encoding="utf-8")
```

Підсистема `importlib.resources` автоматично виявляє наявність `zipimport` завантажувача і зчитує потік байтів безпосередньо з ZIP-архіву без створення тимчасових файлів на диску.

### 3. Пріоритет та безпека списку шляхів `sys.path`

Коли файл запускається як `python app.pyz`, CPython автоматично записує абсолютний шлях до `app.pyz` на позицію `sys.path[0]`. Це гарантує, що будь-які внутрішні імпорти пакунка мають найвищий пріоритет і не будуть перехоплені локальними файлами з поточного робочого каталогу, забезпечуючи детермінованість та безпеку виконання утиліти в різнорідних системних середовищах.
