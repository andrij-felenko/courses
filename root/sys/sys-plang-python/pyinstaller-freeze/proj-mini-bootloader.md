# ⚙️ Реалізація вбудованого завантажувача CPython

Головне завдання нативного завантажувача (англ. *bootloader*, від *bootstrap* — «вушко черевика», та *loader* — «завантажувач», від давньоангл. *hladan* — «вантажити, наповнювати») замороженого застосунку — взяти на себе керування процесом у момент старту операційної системи, підготувати системне середовище для вбудованого інтерпретатора CPython, зареєструвати змінні рантайму, перехопити системні виклики імпорту та передати керування байткоду точки входу. 

У промислових пакувальниках цей механізм містить тисячі рядків коду для роботи з архівами, декомпресією zlib та системними дескрипторами безпеки. Проте фундаментальну архітектуру та порядок ініціалізації середовища можна детально розібрати на автономному робочому завантажувачі мовами C та C++.

## 1. Архітектурна задача та життєвий цикл завантажувача

Коли користувач викликає скомпільований двійковий файл, ядро операційної системи зчитує заголовок ELF або PE і передає потік виконання на точку входу двійкового завантажувача (`main`). Завантажувач мусить виконати строгу послідовність системних операцій до того, як буде виконано перший рядок коду Python:

1. **Визначення власного шляху у файловій системі:** Завантажувач повинен з'ясувати абсолютний шлях до власного двійкового файлу на накопичувачі через спеціалізовані системні виклики ОС (`/proc/self/exe` у Linux, `GetModuleFileNameW` у Windows або `_NSGetExecutablePath` у macOS). Це необхідно, щоб знайти каталог розпакованих бібліотек або відкрити власний файл для вичитування архіву.
2. **Формування ізольованої структури конфігурації CPython (`PyConfig`):** Починаючи з версії CPython 3.8 (стандарт PEP 587), ініціалізація інтерпретатора здійснюється через структуру `PyConfig`. Завантажувач зобов'язаний повністю ізолювати інтерпретатор: вимкнути зчитування змінних середовища хоста (`PYTHONPATH`, `PYTHONHOME`), заблокувати автоматичний імпорт модуля `site` і заборонити пошук глобальних каталогів `site-packages` хостової операційної системи.
3. **Ініціалізація підсистеми CPython у пам'яті процесу:** Виклик `Py_InitializeFromConfig()` створює головний потік інтерпретатора, ініціалізує глобальне блокування інтерпретатора (GIL — *Global Interpreter Lock*), завантажує вбудовані C-модулі (`sys`, `builtins`) і формує базовий простір імен.
4. **Реєстрація маркерів замороженого середовища:** Завантажувач безпосередньо звертається до C-структури модуля `sys` і записує туди атрибути `sys.frozen = True`, `sys._MEIPASS = "/шлях/до/каталогу/ресурсів"` та оновлює `sys.executable`.
5. **Виконання вхідного коду та коректна деініціалізація:** Завантажувач передає керування байткоду вхідної точки, відловлює можливі невиправлені винятки мови Python, транслює код повернення у цілочисельний статус завершення процесу та викликає `Py_Finalize()` для звільнення пам'яті.

## 2. Реалізація завантажувача: C та C++

Нижче наведено повноцінний робочий приклад вбудованого завантажувача, що демонструє безпечну ініціалізацію інтерпретатора, налаштування шляхів та інжекцію маркерів замороженого стану.

:::tabs
```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
  #include <windows.h>
#elif defined(__linux__)
  #include <unistd.h>
  #include <limits.h>
#elif defined(__APPLE__)
  #include <mach-o/dyld.h>
#endif

/* Отримання абсолютного шляху до власного бінарного файлу на диску */
static int get_self_executable_path(wchar_t* out_path, size_t max_len) {
#if defined(_WIN32)
    DWORD len = GetModuleFileNameW(NULL, out_path, (DWORD)max_len);
    return (len > 0 && len < max_len) ? 0 : -1;
#elif defined(__linux__)
    char buf[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (len == -1) return -1;
    buf[len] = '\0';
    if (mbstowcs(out_path, buf, max_len) == (size_t)-1) return -1;
    return 0;
#elif defined(__APPLE__)
    char buf[1024];
    uint32_t size = sizeof(buf);
    if (_NSGetExecutablePath(buf, &size) != 0) return -1;
    if (mbstowcs(out_path, buf, max_len) == (size_t)-1) return -1;
    return 0;
#else
    return -1;
#endif
}

int main(int argc, char* argv[]) {
    PyStatus status;
    PyConfig config;
    wchar_t exe_path[1024];

    /* 1. Визначаємо фізичний шлях до власного бінарного файлу */
    if (get_self_executable_path(exe_path, sizeof(exe_path) / sizeof(wchar_t)) != 0) {
        fprintf(stderr, "[Bootloader Error] Не вдалося з'ясувати шлях до виконуваного файлу.\n");
        return 1;
    }

    /* 2. Ініціалізуємо конфігурацію ізольованого інтерпретатора (PEP 587) */
    PyConfig_InitIsolatedConfig(&config);

    /* Повна ізоляція від середовища хоста */
    config.isolated = 1;          /* Забороняє читати змінні середовища та глобальні шляхи */
    config.use_environment = 0;   /* Ігнорує PYTHONPATH, PYTHONHOME */
    config.site_import = 0;       /* Забороняє імпорт site.py для чистоти простору імен */

    /* Встановлюємо шлях до бінарника як системний executable */
    status = PyConfig_SetString(&config, &config.executable, exe_path);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return 1;
    }

    /* 3. Запуск ініціалізації ядра CPython */
    status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);
    if (PyStatus_Exception(status)) {
        Py_ExitStatusException(status);
    }

    /* 4. Інжектуємо службові змінні sys.frozen та sys._MEIPASS */
    PyObject* sys_mod = PyImport_ImportModule("sys");
    if (!sys_mod) {
        fprintf(stderr, "[Bootloader Error] Критична помилка імпорту модуля sys.\n");
        Py_Finalize();
        return 1;
    }

    /* sys.frozen = True */
    PyObject_SetAttrString(sys_mod, "frozen", Py_True);

    /* sys._MEIPASS = "/шлях/до/каталогу/ресурсів" */
    PyObject* meipass_obj = PyUnicode_FromWideChar(exe_path, -1);
    PyObject_SetAttrString(sys_mod, "_MEIPASS", meipass_obj);
    Py_DECREF(meipass_obj);
    Py_DECREF(sys_mod);

    /* 5. Виконання bootstrap-скрипта (у реальному пакувальнику тут імпорт PYZ-архіву) */
    const char* bootstrap_code =
        "import sys\n"
        "print('[Bootloader C] Інтерпретатор CPython успішно ініціалізовано в пам\\'яті.')\n"
        "print(f'[Bootloader C] sys.frozen = {getattr(sys, \"frozen\", False)}')\n"
        "print(f'[Bootloader C] sys._MEIPASS = {getattr(sys, \"_MEIPASS\", None)}')\n";

    int run_res = PyRun_SimpleString(bootstrap_code);

    /* 6. Коректне завершення рантайму CPython перед виходом */
    Py_Finalize();
    return (run_res == 0) ? 0 : 1;
}
```
```cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <filesystem>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <stdexcept>

#if defined(_WIN32)
  #include <windows.h>
#elif defined(__linux__)
  #include <unistd.h>
  #include <limits.h>
#elif defined(__APPLE__)
  #include <mach-o/dyld.h>
#endif

namespace fs = std::filesystem;

/* RAII-обгортка для суворого керування життєвим циклом ядра CPython */
class PythonRuntimeGuard {
public:
    explicit PythonRuntimeGuard(const fs::path& executable_path) {
        PyConfig config;
        PyConfig_InitIsolatedConfig(&config);

        config.isolated = 1;
        config.use_environment = 0;
        config.site_import = 0;

        auto ws_path = executable_path.wstring();
        PyStatus status = PyConfig_SetString(&config, &config.executable, ws_path.c_str());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося встановити шлях до executable у PyConfig");
        }

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);

        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Аварійна зупинка: виняток під час виклику Py_InitializeFromConfig");
        }
    }

    ~PythonRuntimeGuard() {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    PythonRuntimeGuard(const PythonRuntimeGuard&) = delete;
    PythonRuntimeGuard& operator=(const PythonRuntimeGuard&) = delete;
};

/* Отримання абсолютного шляху до власного двійкового образу процесу */
static fs::path get_executable_path() {
#if defined(_WIN32)
    std::wstring buf(MAX_PATH, L'\0');
    DWORD len = GetModuleFileNameW(nullptr, buf.data(), static_cast<DWORD>(buf.size()));
    if (len == 0) throw std::runtime_error("GetModuleFileNameW завершився з помилкою");
    buf.resize(len);
    return fs::path(buf);
#elif defined(__linux__)
    char buf[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (len == -1) throw std::runtime_error("readlink /proc/self/exe завершився з помилкою");
    buf[len] = '\0';
    return fs::path(buf);
#elif defined(__APPLE__)
    char buf[1024];
    uint32_t size = sizeof(buf);
    if (_NSGetExecutablePath(buf, &size) != 0) throw std::runtime_error("_NSGetExecutablePath failed");
    return fs::canonical(fs::path(buf));
#else
    throw std::runtime_error("Непідтримувана операційна система");
#endif
}

/* Інжекція атрибутів sys.frozen та sys._MEIPASS у простір імен sys */
static void setup_frozen_environment(const fs::path& resource_dir) {
    PyObject* sys_mod = PyImport_ImportModule("sys");
    if (!sys_mod) {
        throw std::runtime_error("Неможливо імпортувати модуль sys");
    }

    // RAII-визволення посилання на об'єкт модуля sys
    auto sys_guard = std::unique_ptr<PyObject, decltype(&Py_DecRef)>(sys_mod, Py_DecRef);

    if (PyObject_SetAttrString(sys_mod, "frozen", Py_True) != 0) {
        throw std::runtime_error("Не вдалося встановити атрибут sys.frozen");
    }

    auto ws_res = resource_dir.wstring();
    PyObject* meipass_obj = PyUnicode_FromWideChar(ws_res.c_str(), -1);
    if (!meipass_obj) {
        throw std::runtime_error("Помилка створення рядка PyUnicode для _MEIPASS");
    }
    auto meipass_guard = std::unique_ptr<PyObject, decltype(&Py_DecRef)>(meipass_obj, Py_DecRef);

    if (PyObject_SetAttrString(sys_mod, "_MEIPASS", meipass_obj) != 0) {
        throw std::runtime_error("Не вдалося встановити атрибут sys._MEIPASS");
    }
}

int main(int argc, char* argv[]) {
    try {
        const fs::path exe_path = get_executable_path();
        const fs::path resource_dir = exe_path.parent_path();

        // 1. Ініціалізація ізольованого рантайму CPython за патерном RAII
        PythonRuntimeGuard runtime(exe_path);

        // 2. Налаштування середовища замороженого застосунку
        setup_frozen_environment(resource_dir);

        // 3. Виконання корисного навантаження
        constexpr std::string_view bootstrap_script =
            "import sys\n"
            "print('[Bootloader C++] Інтерпретатор CPython успішно ініціалізовано в пам\\'яті.')\n"
            "print(f'[Bootloader C++] sys.frozen = {getattr(sys, \"frozen\", False)}')\n"
            "print(f'[Bootloader C++] sys._MEIPASS = {getattr(sys, \"_MEIPASS\", None)}')\n";

        if (PyRun_SimpleString(bootstrap_script.data()) != 0) {
            std::cerr << "[Bootloader Error] Помилка виконання вхідного сценарію.\n";
            return 1;
        }

        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "[Bootloader Fatal] Критичний збій завантажувача: " << ex.what() << '\n';
        return 1;
    }
}
```
:::

## 3. Системний аналіз механізмів та критичних підводних каменів

Розробка нативного завантажувача для вбудованого Python вимагає врахування низки системних факторів, що впливають на стабільність виконання:

### 1. Ізоляція конфігурації через `PyConfig_InitIsolatedConfig`
За замовчуванням інтерпретатор CPython під час старту сканує оточення: шукає змінні `PYTHONPATH` та `PYTHONHOME`, звертається до системного реєстру Windows (`HKEY_LOCAL_MACHINE\Software\Python`) або переглядає стандартні системні шляхи `/usr/lib/python3.x`. Якщо на комп'ютері кінцевого користувача встановлено іншу версію Python, неізольований завантажувач спробує завантажити несумісні файли байткоду стандартної бібліотеки хоста, що спричинить фатальну аварію через несумісність опкодів (*Magic Number Mismatch*). Ізольована конфігурація `config.isolated = 1` повністю блокує будь-які контакти з хостовою системою.

### 2. Специфіка кодування рядків шляхів у Windows
На платформі Windows файлова система NTFS використовує 16-бітне кодування UTF-16LE. Тимчасові каталоги користувачів (`%TEMP%`) часто містять пробіли, символи національних абеток або діакритичні знаки. Використання стандартних однобайтних функцій `char*` призводить до пошкодження рядків шляхів (*Mojibake*). Саме тому завантажувач зобов'язаний оперувати виключно широкими рядками `wchar_t*`, функціями Win32 з суфіксом `W` (`GetModuleFileNameW`) та конвертувати їх у Python-об'єкти через `PyUnicode_FromWideChar`.

### 3. Безпека вивантаження рантайму (`Py_Finalize`)
Функція `Py_Finalize()` виконує повну деініціалізацію: знищує всі створені об'єкти, очищає таблиці інтернованих рядків, звільняє пам'ять та зупиняє внутрішні системні структури. Якщо користувацький застосунок запустив фонові системні потоки (C-threads через сторонні динамічні бібліотеки), виклик `Py_Finalize()` може призвести до взаємного блокування (*Deadlock*) або аварійного збою пам'яті (*Segmentation Fault*), оскільки фонові потоки намагатимуться звернутися до структур GIL, які вже знищено. У зв'язку з цим промислові завантажувачі часто перехоплюють вихід і здійснюють негайне завершення процесу через системні виклики `exit()` або `TerminateProcess()`.

### 4. Встановлення користувацьких завантажувачів байткоду (`sys.meta_path`)
У повноцінному замороженому файлі завантажувач після ініціалізації виконує вбудований байткод модуля `pyimod02_importers.pyc`. Цей скрипт реєструє у списку `sys.meta_path` кастомний шукач `PyZlibArchiveLoader`, який перехоплює будь-які операції `import module_name` і зчитує стиснений байткод безпосередньо з вбудованого PYZ-архіву без звернення до фізичних файлів на диску.

## 4. Інтеграція протоколу імпорту PEP 302 та архітектури ZlibArchive

У реальному замороженому бінарнику завантажувач не розпаковує тисячі `.pyc`-файлів стандартної бібліотеки на диск, оскільки дискові операції створення дрібних файлів різко уповільнюють запуск застосунку. Замість цього використовується вбудований у пам'ять декомпресор.

Механізм роботи кастомного імпортера складається з трьох послідовних кроків:
1. Завантажувач передає відкритий дескриптор файлу або покажчик на замаплений у пам'ять образ архіву спеціальному Python-модулю `pyimod02_importers`.
2. Модуль створює екземпляр класу `PyZlibArchiveLoader`, що реалізує стандартні інтерфейси шукача та завантажувача PEP 302/PEP 451: методи `find_spec(fullname, path, target=None)` та `exec_module(module)`.
3. Коли код викликає інструкцію `import json`, системний механізм імпорту опитує об'єкти в `sys.meta_path`. `PyZlibArchiveLoader` знаходить зміщення байткоду модуля `json` у внутрішньому індексі PYZ-архіву, декомпресує масив байтів за допомогою алгоритму `zlib.decompress()`, викликає функцію `marshal.loads()` для отримання нативного Python Code Object і передає його віртуальній машині через системний виклик `exec(code_object, module.__dict__)`.

Цей підхід забезпечує швидкість імпорту, близьку до швидкості читання оперативної пам'яті, і дозволяє зберігати сотні пітонівських модулів у стисненому стані всередині єдиного бінарного контейнера.

## 5. Багатопотоковість, керування GIL та безпека сигналів

Якщо заморожений застосунок викликає нативні бібліотеки, які створюють власні системні потоки виконання поза середовищем CPython (наприклад, драйвери камер чи аудіопотоки на базі C++), виникає проблема коректного захоплення глобального блокування інтерпретатора GIL.

Перед тим, як будь-який сторонній потік здійснить виклик Python C API, він зобов'язаний зареєструватися в інтерпретаторі через механізм `PyGILState_Ensure()`:

:::tabs
```c
PyGILState_STATE gstate = PyGILState_Ensure();

/* Безпечний виклик функцій Python API з нативного потоку */
PyObject* result = PyObject_CallObject(callback_func, args);
Py_XDECREF(result);

/* Звільнення блокування GIL */
PyGILState_Release(gstate);
```
```cpp
class GilLockGuard {
public:
    GilLockGuard() : state_(PyGILState_Ensure()) {}
    ~GilLockGuard() { PyGILState_Release(state_); }

    GilLockGuard(const GilLockGuard&) = delete;
    GilLockGuard& operator=(const GilLockGuard&) = delete;

private:
    PyGILState_STATE state_;
};

// Використання у робочому коді C++ потоку:
{
    GilLockGuard gil_guard;
    // Безпечний виклик Python C API під захистом RAII
    PyObject* result = PyObject_CallObject(callback_func, args);
    Py_XDECREF(result);
}
```
:::

Завантажувач також налаштовує перехоплення сигналів ОС (`SIGINT`, `SIGTERM`). За замовчуванням CPython встановлює власні обробники сигналів, які встановлюють внутрішній прапорець переривання і перевіряють його між виконанням інструкцій байткоду. Завантажувач гарантує, що отримання сигналу `Ctrl+C` коректно транслюється у виняток `KeyboardInterrupt` у головному потоці Python, дозволяючи контекстним менеджерам та блокам `finally` коректно звільнити системні ресурси.
