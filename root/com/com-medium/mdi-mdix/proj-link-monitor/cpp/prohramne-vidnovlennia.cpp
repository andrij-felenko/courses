// Приклад програмного перезапуску автопогодження на C++20
[[nodiscard]] inline std::expected<void, std::error_code> restart_autoneg(
    const net::SocketHandle& sock, std::string_view ifname) noexcept {
    ethtool_cmd ecmd{};
    ecmd.cmd = ETHTOOL_GSET;

    ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);
    ifr.ifr_data = reinterpret_cast<char*>(&ecmd);

    if (::ioctl(sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ecmd.cmd = ETHTOOL_SSET;
    ecmd.autoneg = AUTONEG_ENABLE;

    if (::ioctl(sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}
