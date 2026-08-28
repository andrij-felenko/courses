/* main_host.c — Запуск модуля Python через C API */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

int run_embedded_module(const char *module_name, int argc, char *argv[]) {
    PyStatus status;
    PyConfig config;

    /* Ініціалізуємо конфігурацію Python за замовчуванням */
    PyConfig_InitPythonConfig(&config);
    config.parse_argv = 1;

    /* Встановлюємо модуль, який буде запущено як точка входу (аналог python -m) */
    status = PyConfig_SetBytesString(&config, &config.run_module, module_name);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Помилка встановлення імені модуля в PyConfig\n");
        return 1;
    }

    /* Передаємо список аргументів командного рядка */
    status = PyConfig_SetBytesArgv(&config, argc, argv);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Помилка встановлення аргументів argv\n");
        return 1;
    }

    /* Розгортаємо структури ядра інтерпретатора */
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        fprintf(stderr, "Фатальна помилка ініціалізації середовища CPython\n");
        return 1;
    }
    PyConfig_Clear(&config);

    /* Запускаємо модуль у контексті __main__ */
    int exit_code = Py_RunMain();
    return exit_code;
}

int main(int argc, char *argv[]) {
    const char *target = (argc > 1) ? argv[1] : "http.server";
    printf("[Host C] Запуск цільового модуля Python: %s\n", target);
    return run_embedded_module(target, argc, argv);
}
