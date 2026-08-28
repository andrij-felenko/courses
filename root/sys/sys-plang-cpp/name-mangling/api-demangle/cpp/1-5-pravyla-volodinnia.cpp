#include <cxxabi.h>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>

void process_symbol_batch_cpp(std::span<const char* const> symbols) {
    size_t capacity = 512;
    std::unique_ptr<char, void(*)(void*)> buffer{
        static_cast<char*>(std::malloc(capacity)),
        std::free
    };
    int status = 0;

    for (size_t i = 0; i < symbols.size(); ++i) {
        char* raw_ptr = buffer.release();
        char* result = abi::__cxa_demangle(symbols[i], raw_ptr, &capacity, &status);
        buffer.reset(result ? result : raw_ptr);

        if (status == 0 && buffer) {
            std::cout << "[" << i << "] " << buffer.get() << '\n';
        } else {
            std::cout << "[" << i << "] " << symbols[i] << " (без змін)\n";
        }
    }
}
