// C++ Implementation: Modern idiomatic mptcpd plugin with RAII & std::expected
#include <iostream>
#include <string_view>
#include <array>
#include <expected>
#include <system_error>
#include <arpa/inet.h>
#include <mptcpd/plugin.h>
#include <mptcpd/pm.h>

namespace mptcp::policy {

class PathPolicyEngine {
public:
    static void on_new_address(mptcpd_pm* pm,
                              uint32_t token,
                              mptcpd_aid_t remote_id,
                              sockaddr const* remote_addr,
                              void* /* user_data */) noexcept 
    {
        auto const addr_info = parse_address(remote_addr);
        if (!addr_info) {
            std::cerr << "[mptcpd-cpp-plugin] Error parsing remote address structure\n";
            return;
        }

        auto const [ip_view, port] = *addr_info;
        std::cout << "[mptcpd-cpp-plugin] Connection 0x" << std::hex << token
                  << std::dec << ": Remote address ID " << static_cast<int>(remote_id)
                  << " -> " << ip_view << ":" << port << "\n";

        // Політика: не створювати підпотік до адрес з ізольованої підмережі
        if (ip_view.starts_with("192.168.99.")) {
            std::cout << "[mptcpd-cpp-plugin] Ignoring subnet 192.168.99.x per policy\n";
            return;
        }

        sockaddr_in local_addr{};
        local_addr.sin_family = AF_INET;
        local_addr.sin_addr.s_addr = INADDR_ANY;

        mptcpd_aid_t constexpr local_id = 0;
        bool constexpr is_backup = false;

        int const err = mptcpd_pm_add_subflow(pm,
                                              token,
                                              local_id,
                                              remote_id,
                                              reinterpret_cast<sockaddr const*>(&local_addr),
                                              remote_addr,
                                              is_backup);
        if (err != 0) {
            std::cerr << "[mptcpd-cpp-plugin] Error ordering subflow: " 
                      << std::generic_category().message(err) << "\n";
        }
    }

private:
    struct EndpointInfo {
        std::string ip;
        uint16_t port;
    };

    static std::expected<EndpointInfo, std::errc> parse_address(sockaddr const* addr) noexcept {
        if (!addr) return std::unexpected(std::errc::invalid_argument);

        std::array<char, INET6_ADDRSTRLEN> buffer{};
        uint16_t port = 0;

        if (addr->sa_family == AF_INET) {
            auto const* in = reinterpret_cast<sockaddr_in const*>(addr);
            if (!inet_ntop(AF_INET, &in->sin_addr, buffer.data(), buffer.size())) {
                return std::unexpected(std::errc::address_family_not_supported);
            }
            port = ntohs(in->sin_port);
        } else if (addr->sa_family == AF_INET6) {
            auto const* in6 = reinterpret_cast<sockaddr_in6 const*>(addr);
            if (!inet_ntop(AF_INET6, &in6->sin6_addr, buffer.data(), buffer.size())) {
                return std::unexpected(std::errc::address_family_not_supported);
            }
            port = ntohs(in6->sin6_port);
        } else {
            return std::unexpected(std::errc::address_family_not_supported);
        }

        return EndpointInfo{ std::string(buffer.data()), port };
    }
};

} // namespace mptcp::policy

extern "C" {
    static mptcpd_plugin_ops const cpp_pm_ops = {
        .new_address = &mptcp::policy::PathPolicyEngine::on_new_address
    };

    MPTCPD_PLUGIN_REGISTER(cpp_custom_policy, &cpp_pm_ops, nullptr, nullptr)
}
