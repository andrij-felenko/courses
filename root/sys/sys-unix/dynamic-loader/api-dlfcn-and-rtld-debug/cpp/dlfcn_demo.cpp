// dlfcn_demo.cpp — Ідіоматичний C++20 RAII wrapper для dlfcn
#include <iostream>
#include <memory>
#include <expected>
#include <string_view>
#include <cmath>
#include <dlfcn.h>

namespace sys {

struct DlHandleDeleter {
    void operator()(void* handle) const noexcept {
        if (handle) {
            ::dlclose(handle);
        }
    }
};

using UniqueDlHandle = std::unique_ptr<void, DlHandleDeleter>;

class DynamicLibrary {
    UniqueDlHandle m_handle;
public:
    static std::expected<DynamicLibrary, std::string> load(std::string_view filename, int flags = RTLD_LAZY) {
        ::dlerror(); // Clear previous errors
        void* handle = ::dlopen(filename.data(), flags);
        if (!handle) {
            const char* err = ::dlerror();
            return std::unexpected(err ? err : "Unknown dlopen error");
        }
        return DynamicLibrary(UniqueDlHandle(handle));
    }

    explicit DynamicLibrary(UniqueDlHandle handle) : m_handle(std::move(handle)) {}

    template <typename FuncPtr>
    std::expected<FuncPtr, std::string> get_symbol(std::string_view symbol_name) const {
        ::dlerror(); // Clear errors
        void* sym = ::dlsym(m_handle.get(), symbol_name.data());
        const char* err = ::dlerror();
        if (err != nullptr) {
            return std::unexpected(std::string(err));
        }
        return reinterpret_cast<FuncPtr>(sym);
    }
};

} // namespace sys

int main() {
    auto lib_result = sys::DynamicLibrary::load("libm.so.6");
    if (!lib_result) {
        std::cerr << "Failed to load library: " << lib_result.error() << '\n';
        return 1;
    }

    auto cos_symbol = lib_result->get_symbol<double(*)(double)>("cos");
    if (!cos_symbol) {
        std::cerr << "Failed to resolve symbol: " << cos_symbol.error() << '\n';
        return 1;
    }

    auto cos_fn = *cos_symbol;
    std::cout << "cos(pi/3) = " << cos_fn(M_PI / 3.0) << '\n';

    return 0;
}
