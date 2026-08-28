// callback_handler.cpp
#include <Python.h>
#include <utility>

namespace py_guard {

class ScopedGILState {
public:
    ScopedGILState() noexcept : state_(PyGILState_Ensure()) {}
    
    ~ScopedGILState() noexcept {
        PyGILState_Release(state_);
    }

    ScopedGILState(const ScopedGILState&) = delete;
    ScopedGILState& operator=(const ScopedGILState&) = delete;
    ScopedGILState(ScopedGILState&&) = delete;
    ScopedGILState& operator=(ScopedGILState&&) = delete;

private:
    PyGILState_STATE state_;
};

} // namespace py_guard

extern "C" void on_hardware_interrupt_cpp(int sensor_id, double value) {
    // Автоматичне захоплення та вивільнення GIL через RAII
    py_guard::ScopedGILState gil_lock;

    PyObject *module = PyImport_ImportModule("telemetry_service");
    if (!module) {
        PyErr_Clear();
        return;
    }

    PyObject *func = PyObject_GetAttrString(module, "on_sensor_event");
    if (func && PyCallable_Check(func)) {
        PyObject *args = Py_BuildValue("(id)", sensor_id, value);
        PyObject *res = PyObject_CallObject(func, args);
        Py_XDECREF(res);
        Py_XDECREF(args);
        Py_DECREF(func);
    }
    Py_DECREF(module);
}
