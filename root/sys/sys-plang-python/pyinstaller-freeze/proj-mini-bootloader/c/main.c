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
