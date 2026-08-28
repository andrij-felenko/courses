#include <cstdio>
#include <cstdlib>
#include <string_view>

namespace {
    struct StreamBufferInitializer {
        StreamBufferInitializer() noexcept {
            if (const char* out_mode = std::getenv("_STDBUF_O")) {
                std::string_view mode{out_mode};
                if (mode == "0") {
                    std::setvbuf(stdout, nullptr, _IONBF, 0);
                } else if (mode == "L") {
                    std::setvbuf(stdout, nullptr, _IOLBF, 0);
                } else {
                    char* end = nullptr;
                    unsigned long sz = std::strtoul(out_mode, &end, 10);
                    if (sz > 0) {
                        std::setvbuf(stdout, nullptr, _IOFBF, sz);
                    }
                }
            }
        }
    };

    // Статичний об'єкт ініціалізується до виклику main()
    const StreamBufferInitializer g_stream_initializer;
}
