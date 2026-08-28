// C++ Interface Abstraction
#include <cstdint>
#include <sys/socket.h>

namespace mptcpd {
    class IPathPlugin {
    public:
        virtual ~IPathPlugin() = default;
        virtual void on_new_connection(uint32_t token) = 0;
        virtual void on_new_address(uint32_t token, uint8_t id, sockaddr const* addr) = 0;
        virtual void on_subflow_closed(uint32_t token) = 0;
    };
}
