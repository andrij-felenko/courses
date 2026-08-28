// safe_logger_c_wrapper.cpp - еквівалентний C++ RAII адаптер
#include <iostream>
#include <string_view>
#include <mutex>

class SafeCppLoggerWrapper {
public:
    static void log(std::string_view msg) {
        std::call_once(s_init_flag, []() {
            s_prefix = "SAFE_CPP_LOG";
            std::cout << "[CPP LOG INIT] " << s_prefix << " активовано\n";
        });
        std::cout << "[" << s_prefix << "] " << msg << "\n";
    }

private:
    static inline std::string_view s_prefix;
    static inline std::once_flag s_init_flag;
};
