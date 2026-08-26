# ⚙️ Створення віртуального імпортера файлів і пам'яті

Під час проектування вбудованих систем, плагінних архітектур, дистрибутивів із захищеним кодом або високопродуктивних тестових стендів виникає потреба завантажувати модулі безпосередньо з оперативної пам'яті, зашифрованих архівів або віддалених сховищ без запису тимчасових файлів на фізичний накопичувач. Збереження модулів на диск у таких сценаріях створює затримки дискового вводу-виводу, відкриває простір для витоку конфіденційного коду та унеможливлює роботу в середовищах із файловими системами, доступними лише для читання (*Read-Only RootFS*).

Реалізація власного знахідника (`MetaPathFinder`) та завантажувача (`Loader`) за стандартом PEP 451 дозволяє безшовно інтегрувати будь-яке віртуальне джерело коду в стандартний конвеєр імпорту CPython.

## 1. Архітектурні вимоги до віртуального завантажувача

Щоб інтерпретатор CPython міг знайти, валідувати та коректно виконати віртуальний модуль, підсистема імпорту вимагає взаємодії двох незалежних об'єктів із простору `importlib.abc`:

1. **Знахідник (`InMemoryFinder`):** реалізує інтерфейс `MetaPathFinder`. Його головний обов'язок — перехопити кваліфіковану назву модуля (`fullname`), перевірити наявність відповідних даних у віртуальному реєстрі та повернути сконфігурований екземпляр `ModuleSpec`.
2. **Завантажувач (`InMemoryLoader`):** реалізує інтерфейс `Loader`. Він приймає створений об'єкт модуля, компілює вихідний текст або десеріалізує готовий байткод і виконує його у словнику простору імен `module.__dict__`.

```
Запит import virtual_pkg.tools
  │
  ▼
[1] Пошук у sys.meta_path:
    InMemoryFinder.find_spec("virtual_pkg.tools", path=["<memory://virtual_pkg>"])
      ├── Перевірка наявності ключа у віртуальному сховищі
      ├── Визначення типу: пакунок (is_pkg=True) чи листовий модуль
      └── Формування та повернення об'єкта ModuleSpec
  │
  ▼
[2] Створення модуля середовищем CPython:
    module = types.ModuleType("virtual_pkg.tools")
    module.__spec__ = spec
    module.__loader__ = spec.loader
    sys.modules["virtual_pkg.tools"] = module  # Реєстрація перед виконанням
  │
  ▼
[3] Виконання коду завантажувачем:
    InMemoryLoader.exec_module(module):
      ├── code_obj = compile(source, origin, "exec")
      └── exec(code_obj, module.__dict__)
```

## 2. Реалізація віртуального імпортера на Python

У наведеній реалізації віртуальне сховище зберігає вихідний код у пам'яті та підтримує як окремі листові модулі, так і багаторівневі пакунки, а також надає методи інтроспекції для стандартних бібліотек `inspect` та `linecache`.

```python
import sys
import types
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec


class InMemoryLoader(Loader):
    """Завантажувач, що транслює та виконує код безпосередньо з оперативної пам'яті."""

    def __init__(self, source_code: str, is_package: bool = False):
        self.source_code = source_code
        self.is_package = is_package

    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        """Створення об'єкта модуля.
        
        Повернення None сигналізує CPython про використання стандартного
        конструктора types.ModuleType(spec.name).
        """
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        """Виконання скомпільованого коду всередині простору імен модуля."""
        origin = module.__spec__.origin or "<virtual-memory>"
        
        # Компіляція вихідного тексту в об'єкт байткоду PyCodeObject
        code_object = compile(
            self.source_code,
            filename=origin,
            mode="exec",
            dont_inherit=True,
            optimize=sys.flags.optimize,
        )

        # Виконання коду у просторі імен створеного модуля
        exec(code_object, module.__dict__)

    def get_source(self, fullname: str) -> str:
        """Повертає вихідний текст модуля для модулів inspect і linecache."""
        return self.source_code

    def get_code(self, fullname: str) -> types.CodeType:
        """Повертає скомпільований PyCodeObject без повторного виклику exec."""
        return compile(self.source_code, f"<memory://{fullname}>", "exec")


class InMemoryFinder(MetaPathFinder):
    """Знахідник мета-шляху для виявлення модулів у віртуальному реєстрі пам'яті."""

    def __init__(self, registry: dict[str, dict]):
        # registry: {"fullname": {"source": "...", "is_pkg": bool}}
        self.registry = registry

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: types.ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Пошук специфікації модуля за повним кваліфікованим ім'ям."""
        if fullname not in self.registry:
            # Модуль не зареєстрований у нашому віртуальному сховищі
            return None

        entry = self.registry[fullname]
        source = entry.get("source", "")
        is_pkg = entry.get("is_pkg", False)

        loader = InMemoryLoader(source_code=source, is_package=is_pkg)
        origin = f"<memory://{fullname}>"

        spec = ModuleSpec(
            name=fullname,
            loader=loader,
            origin=origin,
            is_package=is_pkg,
        )

        # Якщо об'єкт є пакунком, ініціалізуємо список шляхів пошуку підмодулів
        if is_pkg:
            spec.submodule_search_locations = [origin]

        return spec


# Демонстрація підключення та виконання віртуального імпорту
if __name__ == "__main__":
    # Формуємо віртуальне дерево модулів у пам'яті
    virtual_storage = {
        "vpkg": {
            "source": "VERSION = '2.4.0'\nCONFIG = {'mode': 'memory'}",
            "is_pkg": True,
        },
        "vpkg.calc": {
            "source": (
                "import math\n"
                "def hypotenuse(a, b):\n"
                "    return math.sqrt(a**2 + b**2)\n"
            ),
            "is_pkg": False,
        },
    }

    # Реєструємо знахідник на початку sys.meta_path
    importer = InMemoryFinder(virtual_storage)
    sys.meta_path.insert(0, importer)

    # Виконуємо звичайний імпорт
    import vpkg
    from vpkg import calc

    print(f"Імпортовано пакунок: {vpkg.__name__} (v{vpkg.VERSION})")
    distance = calc.hypotenuse(6.0, 8.0)
    print(f"Результат обчислення: {distance}")
    print(f"Специфікація: {calc.__spec__}")
```

## 3. Детальний розбір механізму виконання та ініціалізації

Робота створеного імпортера розгортається у чотири послідовні системні кроки:

1. **Перехоплення запиту:** Коли виконується вираз `from vpkg import calc`, інтерпретатор спершу перевіряє наявність кореневого пакунка `vpkg` у словнику `sys.modules`. Якщо його немає, CPython по черзі опитує знахідники у списку `sys.meta_path`. Оскільки наш екземпляр `InMemoryFinder` додано на нульову позицію, він першим отримує виклик `find_spec("vpkg", None)`.
2. **Формування `ModuleSpec`:** Знахідник знаходить запис у словнику `virtual_storage` і встановлює властивість `is_package = True`. Для пакунків критично заповнити поле `spec.submodule_search_locations`. Це дозволяє CPython зрозуміти, що подальший пошук дочірнього модуля `vpkg.calc` має передавати список шляхів `path=["<memory://vpkg>"]`.
3. **Реєстрація в `sys.modules`:** Середовище виконання CPython створює порожній об'єкт модуля та негайно записує його у `sys.modules["vpkg"] = module`. Це відбувається *до* того, як починає виконуватися будь-який рядок коду всередині модуля. Завдяки цьому, якщо код модуля містить циклічні імпорти або зворотні посилання, інтерпретатор поверне вже створене посилання замість повторного запуску пошуку.
4. **Виконання у просторі імен:** Метод `exec_module` завантажувача викликає вбудовану функцію `compile()`. Параметр `dont_inherit=True` гарантує, що прапорці компіляції викликаючого контексту не вплинуть на компільований модуль, а прапорець `optimize=sys.flags.optimize` забезпечує коректну обробку інструкцій `assert` відповідно до глобальних налаштувань інтерпретатора. Скомпільований об'єкт `PyCodeObject` передається функції `exec()`, яка виконує байткод, заповнюючи словник `module.__dict__`.

## 4. Пряме завантаження серіалізованого байткоду (marshal)

Якщо віртуальне сховище містить не вихідний текст, а попередньо скомпільований байткод (наприклад, видобутий із захищеного бінарного контейнера), компіляцію через `compile()` можна повністю пропустити. Натомість використовується десеріалізація через стандартний модуль `marshal`:

```python
import marshal
import types


class BytecodeInMemoryLoader(InMemoryLoader):
    """Високошвидкісний завантажувач сирого байткоду з пам'яті."""

    def __init__(self, raw_bytecode: bytes, is_package: bool = False):
        super().__init__(source_code="", is_package=is_package)
        self.raw_bytecode = raw_bytecode

    def exec_module(self, module: types.ModuleType) -> None:
        # Десеріалізація об'єкта PyCodeObject з бінарного рядка
        code_object = marshal.loads(self.raw_bytecode)
        
        # Виконання десеріалізованого байткоду
        exec(code_object, module.__dict__)
```

Такий підхід повністю усуває витрати процесорного часу на лексичний аналіз, синтаксичний розбір та побудову абстрактного синтаксичного дерева (AST), скорочуючи час завантаження модуля до часток мікросекунди.

## 5. Імпорт із пам'яті засобами низькорівневого C-API (C та C++)

У вбудованих системах, ігрових рушіях та десктопних програмах на C/C++ Python часто працює як вбудована мова сценаріїв. У такому разі вихідний текст або скомпільований байткод постачаються у вигляді скомпільованих статичних масивів байтів безпосередньо у бінарному файлі програми.

Для завантаження таких ресурсів C-API CPython надає спеціалізовані функції `Py_CompileString` та `PyImport_ExecCodeModule`.

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

/**
 * Імпортує Python-модуль із пам'яті засобами офіційного C-API.
 *
 * @param module_name Повна назва модуля (наприклад, "embedded_math")
 * @param source_code Рядок вихідного тексту Python
 * @return 0 у разі успіху, -1 у разі помилки
 */
int import_module_from_memory(const char *module_name, const char *source_code) {
    // 1. Компіляція вихідного тексту в об'єкт байткоду PyCodeObject
    PyObject *code_obj = Py_CompileString(source_code, "<in-memory-c>", Py_file_input);
    if (!code_obj) {
        PyErr_Print();
        return -1;
    }

    // 2. Створення об'єкта модуля та виконання скомпільованого байткоду
    // PyImport_ExecCodeModule автоматично реєструє модуль у словнику sys.modules
    PyObject *module = PyImport_ExecCodeModule(module_name, code_obj);
    Py_DECREF(code_obj); // Звільняємо посилання на об'єкт коду

    if (!module) {
        PyErr_Print();
        return -1;
    }

    printf("Модуль '%s' успішно зареєстровано в sys.modules\n", module_name);
    Py_DECREF(module); // Зменшуємо лічильник посилань, оскільки sys.modules утримує модуль
    return 0;
}
```
```cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string_view>
#include <memory>
#include <stdexcept>

// RAII-обгортка для автоматичного керування часом життя об'єктів PyObject*
struct PyObjectDeleter {
    void operator()(PyObject* obj) const noexcept {
        if (obj) {
            Py_DECREF(obj);
        }
    }
};

using UniquePyObject = std::unique_ptr<PyObject, PyObjectDeleter>;

/**
 * Ідіоматичний C++20 клас для імпорту модулів із пам'яті через C-API.
 */
class MemoryModuleImporter {
public:
    /**
     * Створює та завантажує модуль у середовище виконання CPython.
     */
    static void import_from_memory(std::string_view module_name, std::string_view source_code) {
        // 1. Компіляція вихідного тексту в об'єкт коду
        UniquePyObject code_obj(Py_CompileString(
            source_code.data(),
            "<in-memory-cpp>",
            Py_file_input
        ));

        if (!code_obj) {
            throw std::runtime_error("Помилка компіляції коду в PyCodeObject");
        }

        // 2. Створення та виконання модуля в пам'яті
        UniquePyObject module(PyImport_ExecCodeModule(
            module_name.data(),
            code_obj.get()
        ));

        if (!module) {
            throw std::runtime_error("Помилка виконання модуля в PyImport_ExecCodeModule");
        }

        std::cout << "Модуль '" << module_name << "' успішно ініціалізовано в C++ оточенні\n";
    }
};
```
:::

## 6. Типові пастки та крайові випадки

При реалізації та експлуатації віртуальних завантажувачів розробники найчастіше стикаються з трьома критичними проблемами:

1. **Некоректне значення `submodule_search_locations`:** Якщо для пакунка не ініціалізувати це поле або встановити його в `None`, CPython розцінить його як звичайний листовий модуль. Спроба імпортувати підмодуль `from vpkg import calc` негайно завершиться помилкою `ModuleNotFoundError: No module named 'vpkg.calc'; 'vpkg' is not a package`.
2. **Обробка винятків під час виконання:** Якщо функція `compile()` або виклик `exec()` зазнає збою через синтаксичну помилку чи виняток часу виконання, інтерпретатор автоматично видаляє напівстворений модуль із `sys.modules`. Не перехоплюйте системні винятки всередині `exec_module` без повторного викидання (`raise`), інакше зламаний модуль залишиться у кеші в неконсистентному стані.
3. **Багатопоточність і стан гонитви:** Якщо кілька потоків операційної системи одночасно намагаються імпортувати один і той самий віртуальний модуль, CPython синхронізує їх за допомогою внутрішніх блокувань підсистеми імпорту. Власне віртуальне сховище (`registry`) має бути потокобезпечним, якщо модулі можуть додаватися або видалятися з нього динамічно під час роботи програми.
4. **Підтримка трасування та налагодження:** Без реалізації методу `get_source()` стандартний форматувальник трасувань стека (*traceback*) не зможе відобразити рядки вихідного коду при виникненні винятків у віртуальних модулях, оскільки файлу фізично не існує на диску. Реалізація `get_source` передає вихідні рядки модулю `linecache`, забезпечуючи інформативні повідомлення про помилки.
