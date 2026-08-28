#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <filesystem>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <stdexcept>

#if defined(_WIN32)
  #include <windows.h>
#elif defined(__linux__)
  #include <unistd.h>
  #include <limits.h>
#elif defined(__APPLE__)
  #include <mach-o/dyld.h>
#endif

namespace fs = std::filesystem;

/* RAII-обгортка для суворого керування життєвим циклом ядра CPython */
class PythonRuntimeGuard {
public:
    explicit PythonRuntimeGuard(const fs::path& executable_path) {
        PyConfig config;
        PyConfig_InitIsolatedConfig(&config);

        config.isolated = 1;
        config.use_environment = 0;
        config.site_import = 0;

        auto ws_path = executable_path.wstring();
        PyStatus status = PyConfig_SetString(&config, &config.executable, ws_path.c_str());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося встановити шлях до executable у PyConfig");
        }

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);

        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Аварійна зупинка: виняток під час виклику Py_InitializeFromConfig");
        }
    }

    ~PythonRuntimeGuard() {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    PythonRuntimeGuard(const PythonRuntimeGuard&) = delete;
    PythonRuntimeGuard& operator=(const PythonRuntimeGuard&) = delete;
};

/* Отримання абсолютного шляху до власного двійкового образу процесу */
static fs::path get_executable_path() {
#if defined(_WIN32)
    std::wstring buf(MAX_PATH, L'\0');
    DWORD len = GetModuleFileNameW(nullptr, buf.data(), static_cast<DWORD>(buf.size()));
    if (len == 0) throw std::runtime_error("GetModuleFileNameW завершився з помилкою");
    buf.resize(len);
    return fs::path(buf);
#elif defined(__linux__)
    char buf[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (len == -1) throw std::runtime_error("readlink /proc/self/exe завершився з помилкою");
    buf[len] = '\0';
    return fs::path(buf);
#elif defined(__APPLE__)
    char buf[1024];
    uint32_t size = sizeof(buf);
    if (_NSGetExecutablePath(buf, &size) != 0) throw std::runtime_error("_NSGetExecutablePath failed");
    return fs::canonical(fs::path(buf));
#else
    throw std::runtime_error("Непідтримувана операційна система");
#endif
}

/* Інжекція атрибутів sys.frozen та sys._MEIPASS у простір імен sys */
static void setup_frozen_environment(const fs::path& resource_dir) {
    PyObject* sys_mod = PyImport_ImportModule("sys");
    if (!sys_mod) {
        throw std::runtime_error("Неможливо імпортувати модуль sys");
    }

    // RAII-визволення посилання на об'єкт модуля sys
    auto sys_guard = std::unique_ptr<PyObject, decltype(&Py_DecRef)>(sys_mod, Py_DecRef);

    if (PyObject_SetAttrString(sys_mod, "frozen", Py_True) != 0) {
        throw std::runtime_error("Не вдалося встановити атрибут sys.frozen");
    }

    auto ws_res = resource_dir.wstring();
    PyObject* meipass_obj = PyUnicode_FromWideChar(ws_res.c_str(), -1);
    if (!meipass_obj) {
        throw std::runtime_error("Помилка створення рядка PyUnicode для _MEIPASS");
    }
    auto meipass_guard = std::unique_ptr<PyObject, decltype(&Py_DecRef)>(meipass_obj, Py_DecRef);

    if (PyObject_SetAttrString(sys_mod, "_MEIPASS", meipass_obj) != 0) {
        throw std::runtime_error("Не вдалося встановити атрибут sys._MEIPASS");
    }
}

int main(int argc, char* argv[]) {
    try {
        const fs::path exe_path = get_executable_path();
        const fs::path resource_dir = exe_path.parent_path();

        // 1. Ініціалізація ізольованого рантайму CPython за патерном RAII
        PythonRuntimeGuard runtime(exe_path);

        // 2. Налаштування середовища замороженого застосунку
        setup_frozen_environment(resource_dir);

        // 3. Виконання корисного навантаження
        constexpr std::string_view bootstrap_script =
            "import sys\n"
            "print('[Bootloader C++] Інтерпретатор CPython успішно ініціалізовано в пам\\'яті.')\n"
            "print(f'[Bootloader C++] sys.frozen = {getattr(sys, \"frozen\", False)}')\n"
            "print(f'[Bootloader C++] sys._MEIPASS = {getattr(sys, \"_MEIPASS\", None)}')\n";

        if (PyRun_SimpleString(bootstrap_script.data()) != 0) {
            std::cerr << "[Bootloader Error] Помилка виконання вхідного сценарію.\n";
            return 1;
        }

        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "[Bootloader Fatal] Критичний збій завантажувача: " << ex.what() << '\n';
        return 1;
    }
}
