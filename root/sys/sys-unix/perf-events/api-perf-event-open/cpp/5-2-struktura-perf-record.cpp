#include <cstdint>
#include <vector>
#include <span>

namespace sys {
    struct ParsedSampleEvent {
        std::uint64_t ip;
        std::uint32_t pid;
        std::uint32_t tid;
        std::uint64_t time;
        std::vector<std::uint64_t> callchain;
    };
}
