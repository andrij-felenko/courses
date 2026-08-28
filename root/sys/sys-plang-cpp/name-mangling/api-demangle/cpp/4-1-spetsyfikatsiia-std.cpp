#include <iostream>
#include <stacktrace>

void trigger_diagnostic() {
    auto trace = std::stacktrace::current();
    std::cout << "--- Діагностичний звіт C++23 ---\n";
    for (const auto& entry : trace) {
        std::cout << entry.description() << " ("
                  << entry.source_file() << ":" << entry.source_line() << ")\n";
    }
}

int main() {
    trigger_diagnostic();
    return 0;
}
