class GilLockGuard {
public:
    GilLockGuard() : state_(PyGILState_Ensure()) {}
    ~GilLockGuard() { PyGILState_Release(state_); }

    GilLockGuard(const GilLockGuard&) = delete;
    GilLockGuard& operator=(const GilLockGuard&) = delete;

private:
    PyGILState_STATE state_;
};

// Використання у робочому коді C++ потоку:
{
    GilLockGuard gil_guard;
    // Безпечний виклик Python C API під захистом RAII
    PyObject* result = PyObject_CallObject(callback_func, args);
    Py_XDECREF(result);
}
