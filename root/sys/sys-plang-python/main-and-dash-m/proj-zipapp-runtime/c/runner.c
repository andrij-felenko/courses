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
