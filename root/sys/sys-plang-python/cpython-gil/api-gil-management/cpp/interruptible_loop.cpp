// interruptible_loop.cpp
#include <Python.h>
#include <cstddef>

int compute_with_signals_cpp(std::size_t total_iterations) noexcept {
    for (std::size_t i = 0; i < total_iterations; i += 10000) {
        Py_BEGIN_ALLOW_THREADS
        // Нативний чисельний розрахунок 10 000 ітерацій
        Py_END_ALLOW_THREADS

        if (PyErr_CheckSignals() != 0) {
            return -1;
        }
    }
    return 0;
}
