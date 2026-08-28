// C++ Idiomatic abstraction of MPTCP endpoint entry
#include <cstdint>
#include <netinet/in.h>

namespace mptcp {
    struct EndpointEntry {
        sockaddr_storage addr{};
        std::uint8_t flags{0};
        std::uint8_t if_index{0};
    };
}
