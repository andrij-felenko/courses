// native_worker.cpp
#include <Python.h>
#include <chrono>
#include <thread>

namespace py_guard {

// RAII обгортка для безпечного керування GIL у стилі сучасного C++
class ScopedAllowThreads {
public:
    ScopedAllowThreads() noexcept : thread_state_(PyEval_SaveThread()) {}
    
    ~ScopedAllowThreads() noexcept {
        if (thread_state_) {
            PyEval_RestoreThread(thread_state_);
        }
    }

    ScopedAllowThreads(const ScopedAllowThreads&) = delete;
    ScopedAllowThreads& operator=(const ScopedAllowThreads&) = delete;
    ScopedAllowThreads(ScopedAllowThreads&& other) noexcept 
        : thread_state_(other.thread_state_) {
        other.thread_state_ = nullptr;
    }
    ScopedAllowThreads& operator=(ScopedAllowThreads&& other) noexcept {
        if (this != &other) {
            if (thread_state_) PyEval_RestoreThread(thread_state_);
            thread_state_ = other.thread_state_;
            other.thread_state_ = nullptr;
        }
        return *this;
    }

private:
    PyThreadState* thread_state_{nullptr};
};

} // namespace py_guard

extern "C" PyObject* long_computation_cpp(PyObject *self, PyObject *args) {
    int duration_sec = 0;
    if (!PyArg_ParseTuple(args, "i", &duration_sec)) {
        return nullptr;
    }

    {
        // Конструктор ScopedAllowThreads відпускає GIL
        py_guard::ScopedAllowThreads allow_threads;

        // C++ код виконується паралельно на рівні ядра ОС
        std::this_thread::sleep_for(std::chrono::seconds(duration_sec));
        
        // Деструктор гарантовано захоплює GIL при виході з блоку або при винятку
    }

    Py_RETURN_NONE;
}
