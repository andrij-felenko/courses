// fast_telemetry.cpp
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <omp.h>

namespace telemetry {

struct alignas(32) TelemetryRecord {
    double gyro_x;
    double gyro_y;
    double gyro_z;
    double temp;
};

void compute_parallel(std::span<const TelemetryRecord> input, std::span<TelemetryRecord> output) noexcept {
    constexpr std::array<double, 3> bias = {0.05, -0.02, 0.01};
    constexpr std::array<std::array<double, 3>, 3> matrix = {{
        {1.02, 0.01, 0.00},
        {0.01, 0.99, -0.01},
        {0.00, 0.02, 1.01}
    }};

    const std::size_t total = input.size();
    #pragma omp parallel for schedule(static)
    for (std::size_t i = 0; i < total; ++i) {
        const auto& in = input[i];
        auto& out = output[i];

        const double r0 = in.gyro_x - bias[0];
        const double r1 = in.gyro_y - bias[1];
        const double r2 = in.gyro_z - bias[2];

        const double c0 = matrix[0][0]*r0 + matrix[0][1]*r1 + matrix[0][2]*r2;
        const double c1 = matrix[1][0]*r0 + matrix[1][1]*r1 + matrix[1][2]*r2;
        const double c2 = matrix[2][0]*r0 + matrix[2][1]*r1 + matrix[2][2]*r2;

        const double t = in.temp;
        const double t_comp = 0.12 + 0.95*t + 0.003*t*t - 0.0001*t*t*t;
        const double factor = 1.0 + 0.001 * t_comp;

        out.gyro_x = c0 * factor;
        out.gyro_y = c1 * factor;
        out.gyro_z = c2 * factor;
        out.temp   = t_comp;
    }
}

} // namespace telemetry

extern "C" {

static PyObject* py_calibrate_fast(PyObject *self, PyObject *args) {
    Py_buffer in_buf{}, out_buf{};
    if (!PyArg_ParseTuple(args, "y*y*", &in_buf, &out_buf)) {
        return nullptr;
    }

    const std::size_t n_records = in_buf.len / sizeof(telemetry::TelemetryRecord);
    auto in_span = std::span<const telemetry::TelemetryRecord>(
        static_cast<const telemetry::TelemetryRecord*>(in_buf.buf), n_records
    );
    auto out_span = std::span<telemetry::TelemetryRecord>(
        static_cast<telemetry::TelemetryRecord*>(out_buf.buf), n_records
    );

    // Звільняємо GIL: обчислення виконуються на всіх ядрах процесора через OpenMP
    Py_BEGIN_ALLOW_THREADS
    telemetry::compute_parallel(in_span, out_span);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&in_buf);
    PyBuffer_Release(&out_buf);
    Py_RETURN_NONE;
}

static PyMethodDef ModuleMethods[] = {
    {"calibrate_fast", py_calibrate_fast, METH_VARARGS, "Швидке калібрування C++ з OpenMP"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef fasttelemetrymodule = {
    PyModuleDef_HEAD_INIT, "fast_telemetry", nullptr, -1, ModuleMethods
};

PyMODINIT_FUNC PyInit_fast_telemetry(void) {
    return PyModule_Create(&fasttelemetrymodule);
}

} // extern "C"
