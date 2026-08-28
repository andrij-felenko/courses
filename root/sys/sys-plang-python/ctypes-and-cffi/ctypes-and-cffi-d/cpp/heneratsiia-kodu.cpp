// Еквівалентна пряма обгортка у C++ модулі розширення
#include <pybind11/pybind11.h>
#include "sensor_driver.hpp"

namespace py = pybind11;

int read_sensor_cpp(SensorData &dev) {
    py::gil_scoped_release release; // RAII-відпускання та захоплення GIL
    return read_sensor(&dev);       // Прямий виклик нативної функції
}
