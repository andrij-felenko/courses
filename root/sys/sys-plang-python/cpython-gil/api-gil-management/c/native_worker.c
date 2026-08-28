// native_worker.c
#include <Python.h>
#include <unistd.h>

PyObject* long_computation_c(PyObject *self, PyObject *args) {
    int duration_sec = 0;
    if (!PyArg_ParseTuple(args, "i", &duration_sec)) {
        return NULL;
    }

    // 1. Відпускаємо GIL перед блокувальною системною операцією
    Py_BEGIN_ALLOW_THREADS

    // Потік виконує чистий C-код. Інтерпретатор Python вільний для інших потоків
    sleep(duration_sec);

    // 2. Обов'язково відновлюємо GIL перед поверненням у Python
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}
