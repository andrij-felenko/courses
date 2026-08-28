// fast_telemetry.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <omp.h>

static void compute_telemetry_c(const double *in_data, double *out_data, size_t n_records) {
    const double bias[3] = {0.05, -0.02, 0.01};
    const double m[3][3] = {
        {1.02, 0.01, 0.00},
        {0.01, 0.99, -0.01},
        {0.00, 0.02, 1.01}
    };

    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n_records; ++i) {
        size_t in_offset = i * 4;
        size_t out_offset = i * 4;

        double r0 = in_data[in_offset + 0] - bias[0];
        double r1 = in_data[in_offset + 1] - bias[1];
        double r2 = in_data[in_offset + 2] - bias[2];

        double c0 = m[0][0]*r0 + m[0][1]*r1 + m[0][2]*r2;
        double c1 = m[1][0]*r0 + m[1][1]*r1 + m[1][2]*r2;
        double c2 = m[2][0]*r0 + m[2][1]*r1 + m[2][2]*r2;

        double temp = in_data[in_offset + 3];
        double temp_comp = 0.12 + 0.95*temp + 0.003*temp*temp - 0.0001*temp*temp*temp;
        double scale_factor = 1.0 + 0.001 * temp_comp;

        out_data[out_offset + 0] = c0 * scale_factor;
        out_data[out_offset + 1] = c1 * scale_factor;
        out_data[out_offset + 2] = c2 * scale_factor;
        out_data[out_offset + 3] = temp_comp;
    }
}

static PyObject* py_calibrate_fast(PyObject *self, PyObject *args) {
    Py_buffer in_buf, out_buf;
    if (!PyArg_ParseTuple(args, "y*y*", &in_buf, &out_buf)) {
        return NULL;
    }

    size_t n_records = in_buf.len / (4 * sizeof(double));
    const double *in_ptr = (const double*)in_buf.buf;
    double *out_ptr = (double*)out_buf.buf;

    // Відпускаємо GIL: дозволяємо інтерпретатору виконувати інші потоки
    Py_BEGIN_ALLOW_THREADS
    compute_telemetry_c(in_ptr, out_ptr, n_records);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&in_buf);
    PyBuffer_Release(&out_buf);
    Py_RETURN_NONE;
}

static PyMethodDef ModuleMethods[] = {
    {"calibrate_fast", py_calibrate_fast, METH_VARARGS, "Швидке калібрування з OpenMP"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fasttelemetrymodule = {
    PyModuleDef_HEAD_INIT, "fast_telemetry", NULL, -1, ModuleMethods
};

PyMODINIT_FUNC PyInit_fast_telemetry(void) {
    return PyModule_Create(&fasttelemetrymodule);
}
