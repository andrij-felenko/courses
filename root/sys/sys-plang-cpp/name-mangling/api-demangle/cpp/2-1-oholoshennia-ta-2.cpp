#include <windows.h>
#include <dbghelp.h>
#include <iostream>
#include <string>
#include <string_view>

std::string win32_undecorate(std::string_view decorated, DWORD flags = UNDNAME_COMPLETE) {
    if (decorated.empty()) {
        return {};
    }
    
    std::string result(1024, '\0');
    DWORD len = UnDecorateSymbolName(
        decorated.data(),
        result.data(),
        static_cast<DWORD>(result.size()),
        flags
    );
    
    if (len == 0 && GetLastError() == ERROR_INSUFFICIENT_BUFFER) {
        result.resize(4096);
        len = UnDecorateSymbolName(
            decorated.data(),
            result.data(),
            static_cast<DWORD>(result.size()),
            flags
        );
    }
    
    if (len > 0) {
        result.resize(len);
        return result;
    }
    return std::string(decorated);
}
