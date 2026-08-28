#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <wchar.h>

/* Безпечна ініціалізація та аудит шляхів пошуку модулів CPython */
int init_safe_embedded_python(const wchar_t* program_name, const wchar_t* custom_lib_path) {
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    config.program_name = Py_DecodeLocale("secure_app", NULL);
    config.isolated = 1;         /* Вмикає повну ізоляцію від середовища */
    config.safe_path = 1;        /* Забороняє додавання CWD до sys.path[0] */
    config.use_environment = 0;  /* Блокує змінні PYTHONPATH та PYTHONHOME */

    status = PyConfig_SetString(&config, &config.program_name, program_name);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return -1;
    }

    /* Явне завдання безпечного списку каталогів пошуку */
    config.module_search_paths_set = 1;
    status = PyWideStringList_Append(&config.module_search_paths, custom_lib_path);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return -1;
    }

    /* Валідація: перевірка, чи не потрапив відносний шлях у список */
    for (size_t i = 0; i < config.module_search_paths.length; i++) {
        const wchar_t* p = config.module_search_paths.items[i];
        if (p[0] != L'/' && p[0] != L'\\' && !(p[0] != L'\0' && p[1] == L':')) {
            fprintf(stderr, "Помилка безпеки: відносний шлях у module_search_paths заборонено!\n");
            PyConfig_Clear(&config);
            return -2;
        }
    }

    status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);

    if (PyStatus_Exception(status)) {
        return -3;
    }
    return 0;
}
