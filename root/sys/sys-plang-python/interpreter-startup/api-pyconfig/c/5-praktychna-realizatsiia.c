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
