// callback_handler.c
#include <Python.h>

void on_hardware_interrupt_c(int sensor_id, double value) {
    // Сторонній потік переривання ОС реєструється в CPython
    PyGILState_STATE gstate = PyGILState_Ensure();

    // Тепер безпечно викликати Python C API
    PyObject *module = PyImport_ImportModule("telemetry_service");
    if (module) {
        PyObject *func = PyObject_GetAttrString(module, "on_sensor_event");
        if (func && PyCallable_Check(func)) {
            PyObject *args = Py_BuildValue("(id)", sensor_id, value);
            PyObject *res = PyObject_CallObject(func, args);
            Py_XDECREF(res);
            Py_DECREF(args);
            Py_DECREF(func);
        }
        Py_DECREF(module);
    }

    // Звільняємо GIL і знищуємо прив'язку потоку
    PyGILState_Release(gstate);
}
