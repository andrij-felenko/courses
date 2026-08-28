// module_definition.c
#include <Python.h>

static PyModuleDef_Slot telemetry_slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED}, // Декларуємо сумісність з free-threaded
    {0, NULL}
};

static struct PyModuleDef telemetry_module = {
    PyModuleDef_HEAD_INIT,
    "telemetry_c",
    "Телеметричний модуль без GIL",
    0,
    NULL,
    telemetry_slots,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_telemetry_c(void) {
    return PyModuleDef_Init(&telemetry_module);
}
