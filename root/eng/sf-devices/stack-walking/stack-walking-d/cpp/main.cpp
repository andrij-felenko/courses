#include <iostream>
#include <vector>
#include <memory>
#include <string_view>
#include <execinfo.h>

namespace diagnostic {

class BacktraceCapture {
public:
    static void print_trace() {
        std::vector<void*> callstack(32);
        const int frames = ::backtrace(callstack.data(), static_cast<int>(callstack.size()));
        
        std::unique_ptr<char*, decltype(&::free)> symbols(
            ::backtrace_symbols(callstack.data(), frames),
            &::free
        );

        if (symbols) {
            for (int i = 0; i < frames; ++i) {
                std::cout << "  [" << i << "] " << std::string_view(symbols.get()[i]) << '\n';
            }
        }
    }
};

} // namespace diagnostic
