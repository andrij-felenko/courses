#include <sys/socket.h>
#include <net/if.h>
#include <cstring>
#include <string_view>

namespace embedded::net {

[[nodiscard]] inline bool bindSocketToInterface(int sockFd, std::string_view ifaceName) noexcept {
    struct ifreq ifr{};
    if (ifaceName.size() >= sizeof(ifr.ifr_name)) {
        return false;
    }
    std::memcpy(ifr.ifr_name, ifaceName.data(), ifaceName.size());
    return setsockopt(sockFd, SOL_SOCKET, SO_BINDTODEVICE, &ifr, sizeof(ifr)) == 0;
}

} // namespace embedded::net
