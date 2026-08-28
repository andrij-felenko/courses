#include <cxxabi.h>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>

std::string demangle(std::string_view mangled) {
    if (mangled.empty()) {
        return {};
    }
    
    int status = 0;
    std::unique_ptr<char, void(*)(void*)> buffer{
        abi::__cxa_demangle(mangled.data(), nullptr, nullptr, &status),
        std::free
    };
    
    if (status == 0 && buffer) {
        return std::string(buffer.get());
    }
    return std::string(mangled);
}
