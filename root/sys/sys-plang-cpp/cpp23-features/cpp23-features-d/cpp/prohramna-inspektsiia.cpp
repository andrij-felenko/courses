#include <stacktrace>
#include <print>

void deep_operation() {
    auto trace = std::stacktrace::current();
    for (const auto& frame : trace) {
        std::println("Функція: {}, файл: {}:{}", 
                     frame.description(), frame.source_file(), frame.source_line());
    }
}
