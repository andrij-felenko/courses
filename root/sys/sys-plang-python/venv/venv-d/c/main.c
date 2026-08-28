#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

/* Ініціалізація CPython з явним підключенням venv через PyConfig */
int run_embedded_venv(const wchar_t *venv_path) {
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    /* Задаємо ізольований префікс середовища */
    status = PyConfig_SetString(&config, &config.prefix, venv_path);
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        return 1;
    }

    /* Дозволяємо виконання site.py для сканування site-packages */
    config.site_import = 1;

    /* Ініціалізуємо середовище CPython */
    status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);
    if (PyStatus_Exception(status)) {
        return 2;
    }

    /* Інтроспекція сформованих шляхів через модуль sys */
    PyObject *sys_mod = PyImport_ImportModule("sys");
    if (!sys_mod) {
        PyErr_Print();
        Py_FinalizeEx();
        return 3;
    }

    PyObject *prefix = PyObject_GetAttrString(sys_mod, "prefix");
    PyObject *base_prefix = PyObject_GetAttrString(sys_mod, "base_prefix");

    if (prefix && base_prefix) {
        PyObject *p_str = PyObject_Str(prefix);
        PyObject *bp_str = PyObject_Str(base_prefix);
        printf("C Runtime: sys.prefix      = %s\n", PyUnicode_AsUTF8(p_str));
        printf("C Runtime: sys.base_prefix = %s\n", PyUnicode_AsUTF8(bp_str));
        Py_XDECREF(p_str);
        Py_XDECREF(bp_str);
    }

    Py_XDECREF(prefix);
    Py_XDECREF(base_prefix);
    Py_DECREF(sys_mod);

    Py_FinalizeEx();
    return 0;
}

int main(void) {
    const wchar_t *env = L"/home/user/project/.venv";
    return run_embedded_venv(env);
}
