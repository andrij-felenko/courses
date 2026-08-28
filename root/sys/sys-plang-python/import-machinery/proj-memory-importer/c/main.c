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
