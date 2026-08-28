// interruptible_loop.c
#include <Python.h>

int compute_with_signals_c(size_t total_iterations) {
    for (size_t i = 0; i < total_iterations; i += 10000) {
        // Виконуємо порцію чисельних розрахунків без GIL
        Py_BEGIN_ALLOW_THREADS
        // Нативний чисельний розрахунок 10 000 ітерацій
        Py_END_ALLOW_THREADS

        // Перевіряємо, чи надійшов сигнал переривання (SIGINT)
        if (PyErr_CheckSignals() != 0) {
            // Сигнал отримано: виняток уже виставлено в інтерпретаторі
            return -1;
        }
    }
    return 0;
}
