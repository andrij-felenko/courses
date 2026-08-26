# 📋 Інтерфейс конфігурації CPython: структура PyConfig і фази ініціалізації

Структура `PyConfig` (впроваджена у PEP 587 для версії Python 3.8+) надає низькорівневий програмний інтерфейс мовою C для точного та безпечного керування процесом ініціалізації середовища виконання CPython. До появи цього інтерфейсу налаштування інтерпретатора здійснювалося через розрізнені глобальні змінні мови C (`Py_NoSiteFlag`, `Py_VerboseFlag`, `Py_IgnoreEnvironmentFlag`, `Py_OptimizeFlag`). Такий підхід створював значні труднощі під час вбудовування CPython у сторонні застосунки: зміна глобального прапорця в одному потоці руйнувала конфігурацію інших інтерпретаторів, виникали стани гонитви під час зчитування системного оточення, а кодування аргументів командного рядка не можна було детерміновано налаштувати до виклику `Py_Initialize()`.

PEP 587 перетворив запуск інтерпретатора на сувору багатофазну машину станів, де всі параметри інкапсульовані в єдиній структурі з чітким протоколом виділення пам'яті, зчитування змінних та обробки виняткових ситуацій.

## 1. Архітектура PEP 587 та фази життєвого циклу

Ініціалізація CPython розділена на дві взаємопов'язані структури: `PyPreConfig` (низькорівнева перед-ініціалізація C-середовища) та `PyConfig` (повна ініціалізація віртуальної машини Python). Такий поділ зумовлений тим, що для коректного зчитування рядків конфігурації інтерпретатору вже потрібні працездатні базові алокатори пам'яті та коректно налаштована системна локаль, яка дозволяє декодувати масиви аргументів `argv` та змінні оточення `envp` у широкі символьні рядки `wchar_t*`.

Повний життєвий цикл конфігурації та запуску складається з п'яти послідовних кроків:

1. **Перед-ініціалізація (`Py_PreInitialize` / `Py_PreInitializeFromBytesArgs`):**
   На цьому етапі CPython налаштовує первинні системні алокатори пам'яті (`PyMem_RawMalloc` та `pymalloc`). Інтерпретатор викликає системну функцію `setlocale(LC_CTYPE, "")`, щоб зчитати мовні налаштування поточної операційної системи. Якщо встановлено режим UTF-8 (PEP 540) або системна локаль визначена як `C` чи `POSIX`, інтерпретатор перемикається на пряме декодування UTF-8, запобігаючи аварійному завершенню при обробці символів за межами набору ASCII.

2. **Створення екземпляра конфігурації:**
   Розробник створює екземпляр структури `PyConfig` і заповнює його значеннями за замовчуванням за допомогою однієї з двох базових функцій: `PyConfig_InitPythonConfig` (стандартна конфігурація для емуляції поведінки утиліти командного рядка `python3`) або `PyConfig_InitIsolatedConfig` (режим повної ізоляції для вбудовування інтерпретатора в C/C++ застосунки).

3. **Модифікація параметрів та зчитування оточення (`PyConfig_Read`):**
   Програмний код застосунку встановлює необхідні прапорці (наприклад, вимикає завантаження `site.py` чи блокує запис байткоду). Функція `PyConfig_Read` зчитує системні змінні оточення та парсить передані аргументи командного рядка, заповнюючи внутрішні списки та прапорці конфігурації.

4. **Атомарний запуск середовища (`Py_InitializeFromConfig`):**
   CPython створює структуру стану інтерпретатора `PyInterpreterState` та стан головного потоку `PyThreadState`. Відбувається реєстрація всіх базових типів, створення системних модулів `builtins`, `sys` та розгортання вбудованої підсистеми імпорту зі статичних C-структур.

5. **Звільнення ресурсів конфігурації (`PyConfig_Clear`):**
   Усі динамічні буфери широких рядків `wchar_t*`, виділені у структурі `PyConfig` під час налаштування, звільняються через системний виклик `PyMem_RawFree`.

## 2. Структура PyStatus та протокол обробки помилок

Усі функції ініціалізації середовища повертають уніфіковану структуру статусу `PyStatus`. Вона дозволяє детерміновано відрізняти успішне виконання операції від фатальної системної помилки або штатного запиту на завершення процесу:

:::tabs
```c
/* Оголошення структури статусу в Include/cpython/pystate.h */
typedef struct {
    enum {
        _PyStatus_TYPE_OK = 0,
        _PyStatus_TYPE_ERROR = 1,
        _PyStatus_TYPE_EXIT = 2
    } _type;
    const char *func;       /* Назва C-функції, де виникла помилка */
    const char *err_msg;    /* Текстовий опис причини відмови */
    int exitcode;           /* Код завершення процесу для передачі в exit() */
} PyStatus;
```
```cpp
/* С++ еквівалент для перевірки стану ініціалізації CPython */
namespace py {

struct Status {
    enum class Type {
        Ok = 0,
        Error = 1,
        Exit = 2
    };

    Type type{Type::Ok};
    std::string function_name{};
    std::string error_message{};
    int exit_code{0};

    [[nodiscard]] bool is_ok() const noexcept { return type == Type::Ok; }
    [[nodiscard]] bool is_error() const noexcept { return type == Type::Error; }
    [[nodiscard]] bool is_exit() const noexcept { return type == Type::Exit; }
};

} // namespace py
```
:::

Протокол обробки статусу вимагає обов'язкової перевірки результату кожного кроку конфігурації:
- Якщо `PyStatus_IsError(status)` повертає ненульове значення, сталася критична помилка (наприклад, не вдалося виділити пам'ять під таблицю типів або знайдено некоректне кодування). У цьому разі слід звільнити тимчасові ресурси викликом `PyConfig_Clear(&config)` і зупинити процес.
- Якщо `PyStatus_IsExit(status)` повертає істину, інтерпретатор штатно виконав інформаційний запит (наприклад, користувач передав аргумент `--help` або `--version`). Програма повинна звільнити пам'ять і завершити процес із кодом `status.exitcode`.

## 3. Керування алокаторами пам'яті: структура PyPreConfig

Структура `PyPreConfig` відповідає за стан середовища до того, як буде створено перший об'єкт Python. Вона ініціалізується функціями `PyPreConfig_InitPythonConfig(&preconfig)` або `PyPreConfig_InitIsolatedConfig(&preconfig)`.

Поле `allocator` визначає, яка саме підсистема виділення пам'яті використовуватиметься ядром CPython:
- `PYMEM_ALLOCATOR_DEFAULT` — стандартні системні функції `malloc`, `realloc`, `free`.
- `PYMEM_ALLOCATOR_PYMALLOC` — оптимізований алокатор пулів і арен для швидкого виділення дрібних об'єктів розміром до 512 байтів.
- `PYMEM_ALLOCATOR_DEBUG` — режим діагностики, який оточує виділені блоки спеціальними байтовими мітками («canaries») для виявлення запису за межі виділеної пам'яті (Buffer Overflow) та подвійного звільнення (Double Free).

Поле `utf8_mode` керує поведінкою кодувань: значення `1` вмикає примусовий режим UTF-8, значення `0` вимикає його, а `-1` активує автоматичний режим, коли CPython аналізує змінні `LC_ALL` та `LANG`.

Поле `dev_mode` активує режим розробника CPython (еквівалент прапорця командного рядка `-X dev`), що вмикає додаткові перевірки структур пам'яті, контроль викликів алокаторів та хуки відстеження витоків `tracemalloc`.

## 4. Повний перелік полів структури PyConfig

Структура `PyConfig` містить параметри поведінки всіх підсистем інтерпретатора. Її поля керують ізоляцією процесу, оптимізацією коду, розрахунком системних шляхів та обробкою аргументів.

### Режими ізоляції та взаємодія із середовищем

Поле `isolated` (ціле число `0` або `1`) є головним перемикачем безпеки. Якщо встановити `config.isolated = 1`, CPython автоматично скидає `use_environment = 0`, `user_site_directory = 0` та встановлює `safe_path = 1`. Це гарантує, що жодні змінні оточення операційної системи та жодні локальні файли в поточному каталозі не зможуть вплинути на поведінку вбудованого середовища.

Поле `use_environment` визначає, чи зчитуватиме CPython змінні `PYTHONHOME`, `PYTHONPATH`, `PYTHONOPTIMIZE` та `PYTHONNOUSERSITE`. При значенні `0` інтерпретатор повністю ігнорує зовнішнє середовище процесу.

Поле `site_import` керує імпортом стандартного модуля `site.py`. Значення `0` (аналог прапорця `-S`) повністю виключає сканування каталогів `site-packages` та виконання `.pth` файлів, що дозволяє скоротити час старту на 15–25 мілісекунд у середовищах із багатьма встановленими пакетами.

Поле `user_site_directory` зі значенням `0` (аналог прапорця `-s`) блокує додавання користувацького каталогу `~/.local/lib/pythonX.Y/site-packages` до системного списку `sys.path`.

Поле `safe_path` зі значенням `1` (прапорець `-P` або змінна `PYTHONSAFEPATH`) забороняє автоматичне додавання поточного робочого каталогу на початок `sys.path`, захищаючи застосунок від атак типу підміни модулів (DLL/Module Hijacking).

### Керування компіляцією та оптимізацією байткоду

Поле `optimization_level` задає ступінь оптимізації генерованого байткоду. Значення `0` відповідає стандартному виконанню; значення `1` (прапорець `-O`) видаляє з коду всі інструкції `assert` та перевірки на основі системного прапорця `__debug__`; значення `2` (прапорець `-OO`) додатково видаляє всі рядки документації `__doc__` для зменшення обсягу оперативної пам'яті.

Поле `write_bytecode` зі значенням `0` (прапорець `-B` або змінна `PYTHONDONTWRITEBYTECODE`) забороняє інтерпретатору зберігати скомпільовані файли байткоду `.pyc` на диску в каталогах `__pycache__`. Це корисно для роботи на файлових системах лише для читання (Read-Only Filesystems).

Поле `verbose` визначає рівень деталізації системного логування імпортів (прапорець `-v`). При значенні `1` або `2` інтерпретатор виводить у потік помилок детальну інформацію про кожен пошук і завантаження файлу.

### Конфігурація шляхів та джерел виконання

Поле `home` (тип `wchar_t*`) дозволяє програмно встановити кореневий каталог встановлення стандартної бібліотеки, замінюючи значення змінної `PYTHONHOME`.

Поле `program_name` задає системне ім'я двійкового файлу, яке згодом відображатиметься у `sys.executable`.

Структура `module_search_paths` типу `PyWideStringList` містить повний список каталогів пошуку модулів `sys.path`. Якщо встановити прапорець `module_search_paths_set = 1`, CPython повністю відключає вбудований алгоритм пошуку орієнтирів (Landmark Search) і використовує виключно переданий набір шляхів.

Поля `run_filename`, `run_command` та `run_module` задають джерело виконання коду: шлях до файлу скрипту, текст команди (прапорець `-c`) або назву модуля для запуску як точки входу (прапорець `-m`).

## 5. Практична реалізація: налаштування та запуск вбудованого інтерпретатора

Нижче наведено порівняння ініціалізації вбудованого інтерпретатора CPython мовами C та C++. Обидва приклади налаштовують ізольоване середовище, вимикають виконання `site.py` для досягнення мінімальної латентності старту та явно задають фіксований шлях `sys.path`.

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    PyStatus status;
    PyConfig config;

    /* 1. Ініціалізація структури ізольованою базовою конфігурацією */
    PyConfig_InitIsolatedConfig(&config);

    /* 2. Налаштування параметрів для швидкого та детермінованого старту */
    config.site_import = 0;        /* Вимкнути site.py для мінімізації дискового I/O */
    config.write_bytecode = 0;     /* Заборонити генерацію файлів __pycache__ */
    config.safe_path = 1;          /* Заборонити імпорт із поточного каталогу */

    /* 3. Встановлення ідентифікатора програми */
    status = PyConfig_SetString(&config, &config.program_name, L"embedded_cpython_host");
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        Py_ExitStatusException(status);
    }

    /* 4. Явне перевизначення системних шляхів sys.path */
    config.module_search_paths_set = 1;
    status = PyWideStringList_Append(&config.module_search_paths, L"/usr/lib/python3.12");
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        Py_ExitStatusException(status);
    }

    /* 5. Атомарна ініціалізація середовища виконання CPython */
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        Py_ExitStatusException(status);
    }

    /* 6. Звільнення динамічних буферів структури конфігурації */
    PyConfig_Clear(&config);

    /* 7. Виконання коду у підготовленому ізольованому середовищі */
    PyRun_SimpleString("import sys\n"
                       "print(f'[C Host] CPython online. sys.path: {sys.path}')\n"
                       "print(f'[C Host] site_import status: {sys.flags.no_site}')\n");

    /* 8. Фіналізація та коректне вивільнення ресурсів інтерпретатора */
    Py_Finalize();
    return 0;
}
```
```cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace py {

/* RAII-обгортка над ресурсами структури PyConfig */
class ScopedConfig {
public:
    explicit ScopedConfig(bool isolated = true) {
        if (isolated) {
            PyConfig_InitIsolatedConfig(&config_);
        } else {
            PyConfig_InitPythonConfig(&config_);
        }
    }

    ~ScopedConfig() noexcept {
        PyConfig_Clear(&config_);
    }

    ScopedConfig(const ScopedConfig&) = delete;
    ScopedConfig& operator=(const ScopedConfig&) = delete;
    ScopedConfig(ScopedConfig&&) noexcept = delete;
    ScopedConfig& operator=(ScopedConfig&&) noexcept = delete;

    PyConfig& get() noexcept { return config_; }

    void set_program_name(const std::wstring& name) {
        check_status(PyConfig_SetString(&config_, &config_.program_name, name.c_str()));
    }

    void set_search_paths(const std::vector<std::wstring>& paths) {
        config_.module_search_paths_set = 1;
        for (const auto& path : paths) {
            check_status(PyWideStringList_Append(&config_.module_search_paths, path.c_str()));
        }
    }

    void initialize_runtime() {
        check_status(Py_InitializeFromConfig(&config_));
    }

private:
    PyConfig config_;

    static void check_status(const PyStatus& status) {
        if (PyStatus_Exception(status)) {
            if (status.err_msg) {
                throw std::runtime_error(std::string("CPython Init Error: ") + status.err_msg);
            }
            throw std::runtime_error("CPython Init Error (exit code " + std::to_string(status.exitcode) + ")");
        }
    }
};

/* RAII-обгортка над середовищем виконання CPython */
class ScopedRuntime {
public:
    explicit ScopedRuntime(ScopedConfig& config) {
        config.initialize_runtime();
    }

    ~ScopedRuntime() noexcept {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    ScopedRuntime(const ScopedRuntime&) = delete;
    ScopedRuntime& operator=(const ScopedRuntime&) = delete;
    ScopedRuntime(ScopedRuntime&&) noexcept = delete;
    ScopedRuntime& operator=(ScopedRuntime&&) noexcept = delete;

    void execute(const std::string& script) const {
        if (PyRun_SimpleString(script.c_str()) != 0) {
            throw std::runtime_error("Python execution failed");
        }
    }
};

} // namespace py

int main() {
    try {
        py::ScopedConfig config(true);
        config.get().site_import = 0;
        config.get().write_bytecode = 0;
        config.get().safe_path = 1;

        config.set_program_name(L"embedded_cpp_runtime_host");
        config.set_search_paths({L"/usr/lib/python3.12"});

        py::ScopedRuntime runtime(config);
        runtime.execute("import sys\n"
                        "print(f'[C++ Host] Runtime online. sys.path: {sys.path}')\n"
                        "print(f'[C++ Host] no_site flag: {sys.flags.no_site}')\n");
    } catch (const std::exception& ex) {
        std::cerr << "CPython initialization error: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## 6. Підводні камені та типові помилки конфігурації

Під час роботи з низькорівневим інтерфейсом `PyConfig` розробники найчастіше стикаються з трьома критичними проблемами керування пам'яттю та станом:

1. **Передчасний виклик `PyConfig_Clear` (Use-After-Free):**
   Функція `PyConfig_SetString` та маніпулятори списків виділяють широкі рядки `wchar_t*` через системний алокатор `PyMem_RawMalloc`. Виклик `PyConfig_Clear` звільняє ці буфери. Якщо викликати очищення структури до виклику `Py_InitializeFromConfig`, інтерпретатор отримає вказівники на вже звільнену пам'ять, що призведе до аварійного завершення процесу (Segmentation Fault).

2. **Конфлікт ізольованого режиму та змінних оточення:**
   Встановлення прапорця `config.isolated = 1` автоматично скидає `config.use_environment = 0`. У цьому режимі інтерпретатор повністю проігнорує змінні `PYTHONPATH` та `PYTHONHOME`. Якщо застосунку потрібні додаткові каталоги бібліотек, їх слід обов'язково передати програмно через список `config.module_search_paths`.

3. **Кодування та обробка рядків широких символів:**
   Усі рядкові поля у структурі `PyConfig` вимагають типу `wchar_t*`. Для передачі звичайних рядків UTF-8 типу `const char*` необхідно обов'язково використовувати допоміжну функцію `PyConfig_SetBytesString(&config, &config.field, utf8_string)`. Пряме приведення типів або використання нестандартних функцій конвертації призведе до спотворення шляхів на операційних системах із відмінними від UTF-8 локалями.
