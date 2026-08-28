#include <pybind11/pybind11.h>
#include "cantor.hpp"

namespace py = pybind11;

PYBIND11_MODULE(libcantor, m) {
    m.doc() = "High-performance C++20 Cantor set computation module";
    
    m.def("contains", &math::fractals::CantorGenerator::contains_point,
          py::arg("x"), py::arg("max_depth") = 30,
          "Check if point x belongs to Cantor set");
}
