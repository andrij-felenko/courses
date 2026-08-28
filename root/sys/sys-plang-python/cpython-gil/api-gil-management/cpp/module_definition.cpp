// module_definition.cpp
#include <Python.h>
#include <array>

namespace {

constexpr std::array<PyModuleDef_Slot, 2> module_slots = {{
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, nullptr}
}};

PyModuleDef telemetry_module = {
    PyModuleDef_HEAD_INIT,
    "telemetry_cpp",
    "Телеметричний C++ модуль без GIL",
    0,
    nullptr,
    const_cast<PyModuleDef_Slot*>(module_slots.data()),
    nullptr,
    nullptr,
    nullptr
};

} // namespace

extern "C" PyMODINIT_FUNC PyInit_telemetry_cpp(void) {
    return PyModule_Create(&telemetry_module);
}
