# ⚙️ Компіляція бінарного wheel із C-розширенням та виправленням RPATH

Створення самодостатнього бінарного колеса (`wheel`) для C-розширення вимагає розв'язання комплексу низькорівневих системних задач: взаємодії з Python/C API, компіляції вихідного коду у спільну бібліотеку ELF, ізоляції сторонніх динамічних залежностей через керування шляхами завантажувача (`RPATH` / `RUNPATH`) та формування ZIP-архіву з криптографічними контрольними сумами за стандартами PEP 425, PEP 427 та PEP 627.

## 1. Системний контекст та модель пам'яті C-розширення

Спільний об'єкт розширення (`.so` в Linux) взаємодіє з інтерпретатором CPython через двійковий інтерфейс ABI. Під час виклику функцій інтерпретатор передає покажчики на внутрішні структури `PyObject`.

Для забезпечення максимальної продуктивності обчислень розширення використовує протокол буфера (Buffer Protocol, PEP 3118). Замість повільного копіювання пітонівських об'єктів у проміжні масиви C-розширення захоплює прямий покажчик на неперервний блок оперативної пам'яті (наприклад, масив `bytes` або `bytearray`) через структуру `Py_buffer`.

Макроси та вирівнювання:
- Директива `#define PY_SSIZE_T_CLEAN` перед включенням `<Python.h>` повідомляє компілятору, що парсер форматних рядків `PyArg_ParseTuple` повинен використовувати тип `Py_ssize_t` замість застарілого `int` для обчислення довжини буферів, що запобігає переповненню розрядності на 64-бітних архітектурах.
- Захоплення буфера через форматний специфікатор `y*` вимагає обов'язкового виклику `PyBuffer_Release()` у кожній гілці завершення функції, включно з обробкою помилок, щоб запобігти витоку пам'яті та блокуванню виділених сторінок.

Нижче наведено реалізацію обчислення скалярного добутку векторів: версія C демонструє пряме керування ресурсами, а версія C++ використовує ідіому RAII для гарантованого автоматичного звільнення буферів через деструктор та безпечні діапазони `std::span`.

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>

/* Функція з зовнішньої бібліотеки libengine.so */
extern double compute_dot_product(const double* a, const double* b, size_t n);

static PyObject* py_dot_product(PyObject* self, PyObject* args) {
    Py_buffer buf_a;
    Py_buffer buf_b;

    if (!PyArg_ParseTuple(args, "y*y*", &buf_a, &buf_b)) {
        return NULL;
    }

    if (buf_a.len != buf_b.len || (buf_a.len % sizeof(double)) != 0) {
        PyBuffer_Release(&buf_a);
        PyBuffer_Release(&buf_b);
        PyErr_SetString(PyExc_ValueError, "Buffers must be of equal size and aligned to sizeof(double)");
        return NULL;
    }

    size_t count = (size_t)buf_a.len / sizeof(double);
    const double* ptr_a = (const double*)buf_a.buf;
    const double* ptr_b = (const double*)buf_b.buf;

    double result = compute_dot_product(ptr_a, ptr_b, count);

    PyBuffer_Release(&buf_a);
    PyBuffer_Release(&buf_b);

    return PyFloat_FromDouble(result);
}

static PyMethodDef FastMathMethods[] = {
    {"dot_product", py_dot_product, METH_VARARGS, "Compute dot product of two raw double buffers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    "High performance vector math module",
    -1,
    FastMathMethods
};

PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
```
```cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <span>
#include <vector>
#include <memory>
#include <string_view>

/* Функція з зовнішньої бібліотеки libengine.so */
extern "C" double compute_dot_product(const double* a, const double* b, size_t n);

namespace fastmath {

class PyBufferGuard {
public:
    explicit PyBufferGuard(Py_buffer& buf) noexcept : buf_(buf) {}
    ~PyBufferGuard() noexcept { PyBuffer_Release(&buf_); }
    PyBufferGuard(const PyBufferGuard&) = delete;
    PyBufferGuard& operator=(const PyBufferGuard&) = delete;

private:
    Py_buffer& buf_;
};

static PyObject* dot_product(PyObject* /* self */, PyObject* args) {
    Py_buffer raw_a{};
    Py_buffer raw_b{};

    if (!PyArg_ParseTuple(args, "y*y*", &raw_a, &raw_b)) {
        return nullptr;
    }

    PyBufferGuard guard_a(raw_a);
    PyBufferGuard guard_b(raw_b);

    if (raw_a.len != raw_b.len || (raw_a.len % sizeof(double)) != 0) {
        PyErr_SetString(PyExc_ValueError, "Buffers must be of equal size and aligned to sizeof(double)");
        return nullptr;
    }

    const size_t count = static_cast<size_t>(raw_a.len) / sizeof(double);
    std::span<const double> span_a(static_cast<const double*>(raw_a.buf), count);
    std::span<const double> span_b(static_cast<const double*>(raw_b.buf), count);

    double result = compute_dot_product(span_a.data(), span_b.data(), span_a.size());
    return PyFloat_FromDouble(result);
}

} // namespace fastmath

static PyMethodDef FastMathMethods[] = {
    {"dot_product", fastmath::dot_product, METH_VARARGS, "Compute dot product of two raw double buffers"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    "High performance vector math module (C++ backend)",
    -1,
    FastMathMethods
};

extern "C" PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
```
:::

## 2. Механіка лінкування та розв'язання залежностей через RPATH

Коли компілятор збирає модуль розширення `_fastmath.so`, він зв'язує його з допоміжною динамічною бібліотекою `libengine.so`. За замовчуванням лінкер записує в секцію `.dynamic` заголовок `DT_NEEDED: libengine.so`.

Під час встановлення колеса на комп'ютер користувача бібліотека `libengine.so` опиняється всередині каталогу `site-packages`, а не у системних шляхах `/usr/lib` або `/lib64`. Коли користувач викликає `import fastmath`, динамічний завантажувач Linux `ld.so` намагається завантажити `_fastmath.so` за допомогою системного виклику `dlopen()`. Оскільки системні каталоги не містять `libengine.so`, виникає аварійна помилка завантаження.

Для розв'язання цієї проблеми інструмент збирання модифікує заголовок `DT_RUNPATH` двійкового файлу за допомогою утиліти `patchelf`:
1. Встановлює значення `DT_RUNPATH` рівним `$ORIGIN/fastmath.libs`. Макрос `$ORIGIN` інтерпретується завантажувачем `ld.so` під час виконання як абсолютний фізичний каталог, у якому розміщено сам файл `_fastmath.so`.
2. Змінює внутрішнє ім'я `soname` бібліотеки `libengine.so` на унікальний ідентифікатор (наприклад, `libengine-fastmath.so.1`), щоб уникнути конфліктів із системними версіями однойменних бібліотек.

```
site-packages/
├── fastmath/
│   ├── __init__.py
│   └── _fastmath.cpython-312-x86_64-linux-gnu.so  [DT_RUNPATH: $ORIGIN/fastmath.libs]
└── fastmath.libs/
    └── libengine-fastmath.so.1                   [Ізольована бібліотека]
```

### Порівняння механізмів відносних шляхів між операційними системами

Кожна операційна система має власний механізм пошуку динамічних бібліотек, розгорнутих усередині коліс:
- **Linux (ELF):** використовує динамічний макрос `$ORIGIN` у заголовках `DT_RUNPATH` або `DT_RPATH`. Пошук виконується ядром динамічного лінкера `ld-linux.so`.
- **macOS (Mach-O):** використовує завантажувальні токени `@loader_path` (каталог завантажуваного модуля) або `@rpath` (динамічний стек шляхів пошуку). Модифікація здійснюється системною утилітою Apple `install_name_tool -change` та `install_name_tool -add_rpath`, якою автоматично керує інструмент `delocate`.
- **Windows (PE/COFF):** бінарний формат PE не має аналога RPATH у заголовках. Завантажувач Windows шукає DLL у каталозі виконуваного файлу (`python.exe`), але не у підкаталогах `site-packages`. Тому в Python 3.8+ пакет під час ініціалізації в `__init__.py` повинен викликати функцію `os.add_dll_directory()`, або всі залежні DLL мають копіюватися у той самий каталог, де лежить файл `.pyd` (що автоматично виконує утиліта `delvewheel`).

## 3. Забезпечення детермінованості збирання (Reproducible Builds)

Стандарт ZIP-архівації фіксує мітку часу модифікації для кожного файлу у форматі MS-DOS (двосекундна точність). Якщо зібрати той самий wheel-пакет двічі з інтервалом у кілька секунд, бінарні дайджести отриманих архівів `.whl` будуть різними через зміну часових міток у заголовках ZIP, навіть якщо скомпільований C-код байт-у-байт ідентичний.

Для досягнення **детермінованого збирання** (Reproducible Builds) інструменти пакування:
1. Зчитують стандартизовану змінну оточення `SOURCE_DATE_EPOCH` (Unix-час у секундах останнього git-коміту).
2. Нормалізують дату модифікації всіх файлів в архіві до фіксованої мітки часу (наприклад, `1980-01-01 00:00:00 UTC` за стандартом PEP 552).
3. Сортують файли у маніфесті та структурі ZIP за лексикографічним порядком шляхів.
4. Фіксують права доступу POSIX: `0755` (rwxr-xr-x) для спільних бібліотек `.so` та `0644` (rw-r--r--) для текстових файлів коду й метаданих.

## 4. Діагностика та автоматизація в CI/CD

Після створення колеса інженер може перевірити коректність роботи шляхів пошуку бібліотек без розгортання всього оточення. Для цього застосовується вбудована налагоджувальна функція динамічного завантажувача Linux через змінну оточення `LD_DEBUG`:

```bash
# Трасування пошуку бібліотек під час імпорту
LD_DEBUG=libs,files python3 -c "import fastmath"
```

У виводі налагоджувача буде чітко видно, як завантажувач розкриває макрос `$ORIGIN`:
```
find library=libengine-fastmath.so.1 [0]; searching
 search path=/home/user/project/fastmath/fastmath.libs (RUNPATH from file /home/user/project/fastmath/_fastmath.so)
  trying file=/home/user/project/fastmath/fastmath.libs/libengine-fastmath.so.1
```

У промислових проектах ручне збирання замінюють автоматизованим конвеєром **`cibuildwheel`**. Ця утиліта запускає матрицю збірок у спеціалізованих Docker-контейнерах `manylinux` та `musllinux`, емулюючи цільові архітектури (aarch64, s390x, ppc64le) через QEMU, виконує компіляцію під усі версії CPython та викликає `auditwheel repair` для кожного зібраного колеса в автоматичному режимі.

## 5. Автоматизований збирач колеса мовою Python

Нижче наведено повний скрипт збирача, який виконує компіляцію, ізоляцію динамічних бібліотек, розрахунок контрольних сум SHA-256 та упаковування валідного архіву `.whl`:

```py
import base64
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from pathlib import Path

PKG_NAME = "fastmath"
VERSION = "1.0.0"
PYTHON_TAG = f"cp{sys.version_info.major}{sys.version_info.minor}"
ABI_TAG = f"cp{sys.version_info.major}{sys.version_info.minor}"
PLATFORM_TAG = "manylinux_2_28_x86_64"
WHEEL_NAME = f"{PKG_NAME}-{VERSION}-{PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}.whl"


def compile_and_patch_binaries(build_dir: Path) -> Path:
    """Скомпілювати C-розширення та налаштувати RUNPATH через patchelf."""
    py_include = sysconfig.get_path("include")
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    pkg_dir = build_dir / PKG_NAME
    libs_dir = pkg_dir / "fastmath.libs"
    libs_dir.mkdir(parents=True, exist_ok=True)

    engine_so = libs_dir / "libengine.so"
    output_so = pkg_dir / f"_fastmath{ext_suffix}"

    # 1. Компіляція допоміжної бібліотеки libengine.so
    subprocess.run([
        "gcc", "-O3", "-shared", "-fPIC",
        "-o", str(engine_so),
        "src/engine.c",
        f"-Wl,-soname,libengine-{PKG_NAME}.so.1"
    ], check=True)

    # 2. Компіляція C-розширення Python
    subprocess.run([
        "gcc", "-O3", "-shared", "-fPIC",
        f"-I{py_include}",
        "-o", str(output_so),
        "src/fastmath.c",
        f"-L{libs_dir}", "-lengine"
    ], check=True)

    # 3. Модифікація ELF заголовків: прив'язка до $ORIGIN
    subprocess.run([
        "patchelf",
        "--set-rpath", "$ORIGIN/fastmath.libs",
        "--replace-needed", "libengine.so", f"libengine-{PKG_NAME}.so.1",
        str(output_so)
    ], check=True)

    # 4. Створення пітонівського пакету
    (pkg_dir / "__init__.py").write_text(
        "from ._fastmath import dot_product\n__all__ = ['dot_product']\n",
        encoding="utf-8"
    )

    return output_so


def generate_metadata_and_record(build_dir: Path) -> None:
    """Створити каталог .dist-info з метаданими та маніфестом RECORD."""
    dist_info = build_dir / f"{PKG_NAME}-{VERSION}.dist-info"
    dist_info.mkdir(parents=True, exist_ok=True)

    # 1. Генерація METADATA
    metadata_content = (
        "Metadata-Version: 2.3\n"
        f"Name: {PKG_NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: High performance vector math native extension\n"
        "Requires-Python: >=3.9\n"
        "Description-Content-Type: text/markdown\n\n"
        "# FastMath\nNative vector computation module."
    )
    (dist_info / "METADATA").write_text(metadata_content, encoding="utf-8")

    # 2. Генерація WHEEL
    wheel_content = (
        "Wheel-Version: 1.0\n"
        "Generator: custom-wheel-builder 1.0\n"
        "Root-Is-Purelib: false\n"
        f"Tag: {PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}\n"
    )
    (dist_info / "WHEEL").write_text(wheel_content, encoding="utf-8")

    # 3. Розрахунок криптографічного маніфесту RECORD
    record_rel_path = f"{PKG_NAME}-{VERSION}.dist-info/RECORD"
    rows: list[tuple[str, str, str | int]] = []

    for file_path in sorted(build_dir.rglob("*")):
        if file_path.is_file():
            rel = file_path.relative_to(build_dir).as_posix()
            if rel == record_rel_path:
                continue
            data = file_path.read_bytes()
            digest = hashlib.sha256(data).digest()
            hash_b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
            rows.append((rel, f"sha256={hash_b64}", len(data)))

    # Запис самого RECORD без хешу
    rows.append((record_rel_path, "", ""))

    with open(dist_info / "RECORD", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def build_final_wheel_archive(build_dir: Path, output_file: Path) -> None:
    """Запакувати результат у детермінований ZIP-архів wheel."""
    with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(build_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir).as_posix()
                # Встановлення фіксованих дозволів на файли (0755 для бінарників, 0644 для тексту)
                zinfo = zipfile.ZipInfo.from_file(file_path, arcname=arcname)
                # Нормалізація дати до 1980-01-01 для детермінованого SHA-256 архіву
                zinfo.date_time = (1980, 1, 1, 0, 0, 0)
                if file_path.suffix in [".so", ".pyd", ".dylib"]:
                    zinfo.external_attr = 0o755 << 16
                else:
                    zinfo.external_attr = 0o644 << 16
                
                with open(file_path, "rb") as f:
                    zf.writestr(zinfo, f.read())
    
    print(f"Успішно зібрано бінарний архів: {output_file}")
```
