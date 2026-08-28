#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <wchar.h>

/* Витягування та друк розрахованого списку sys.path через структуру PyConfig */
int inspect_cpython_path_configuration(void) {
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    /* Зчитування системної конфігурації з урахуванням оточення процесу */
    status = PyConfig_Read(&config);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return -1;
    }

    wprintf(L"Кількість розрахованих шляхів пошуку: %zu\n", config.module_search_paths.length);
    for (size_t i = 0; i < config.module_search_paths.length; i++) {
        wprintf(L"  [%zu] %ls\n", i, config.module_search_paths.items[i]);
    }

    /* Звільнення виділених C-структур без запуску повного runtime */
    PyConfig_Clear(&config);
    return 0;
}
