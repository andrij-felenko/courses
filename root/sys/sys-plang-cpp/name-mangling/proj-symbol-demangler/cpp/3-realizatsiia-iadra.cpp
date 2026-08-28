#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <utility>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")
#else
#include <cxxabi.h>
#endif

class SymbolDemangler {
public:
    explicit SymbolDemangler(size_t initial_capacity = 512)
        : capacity_(initial_capacity),
          buffer_(static_cast<char*>(std::malloc(initial_capacity)), std::free) {}

    SymbolDemangler(const SymbolDemangler&) = delete;
    SymbolDemangler& operator=(const SymbolDemangler&) = delete;
    SymbolDemangler(SymbolDemangler&&) noexcept = default;
    SymbolDemangler& operator=(SymbolDemangler&&) noexcept = default;

    std::string demangle(std::string_view mangled) {
        if (mangled.empty()) {
            return {};
        }

#if defined(_WIN32)
        std::string result(1024, '\0');
        DWORD flags = UNDNAME_NO_MS_KEYWORDS | UNDNAME_NO_ACCESS_SPECIFIERS;
        DWORD len = UnDecorateSymbolName(
            mangled.data(),
            result.data(),
            static_cast<DWORD>(result.size()),
            flags
        );
        if (len > 0) {
            result.resize(len);
            return result;
        }
#else
        std::string_view target = mangled;
        if (target.starts_with("__Z")) {
            target.remove_prefix(1);
        }

        // Швидкий шлях: якщо символ не починається з _Z, це не Itanium C++
        if (!target.starts_with("_Z")) {
            return std::string(mangled);
        }

        int status = 0;
        char* raw_ptr = buffer_.release();
        char* demangled = abi::__cxa_demangle(target.data(), raw_ptr, &capacity_, &status);
        buffer_.reset(demangled ? demangled : raw_ptr);

        if (status == 0 && buffer_) {
            return std::string(buffer_.get());
        }
#endif
        return std::string(mangled);
    }

private:
    size_t capacity_;
    std::unique_ptr<char, void(*)(void*)> buffer_;
};
