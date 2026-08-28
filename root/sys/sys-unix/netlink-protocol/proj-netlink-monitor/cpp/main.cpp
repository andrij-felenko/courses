#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <system_error>
#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>
#include <poll.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>

// RAII-обгортка для файлового дескриптора сокета
class UniqueFd {
    int m_fd{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            close(m_fd);
        }
        m_fd = new_fd;
    }
};

class NetlinkMonitor {
    UniqueFd m_sock;
    static constexpr size_t BufferSize = 8192;

public:
    NetlinkMonitor() {
        int fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }
        m_sock.reset(fd);

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_pid = 0;
        sa.nl_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR;

        if (::bind(m_sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to bind netlink socket");
        }
    }

    void run() {
        std::cout << "C++20 Netlink Monitor started. Waiting for events...\n";
        std::vector<uint8_t> buffer(BufferSize);
        pollfd pfd{ .fd = m_sock.get(), .events = POLLIN, .revents = 0 };

        while (true) {
            int ret = ::poll(&pfd, 1, -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "poll failed");
            }

            if (pfd.revents & POLLIN) {
                ssize_t bytes_read = ::recv(m_sock.get(), buffer.data(), buffer.size(), 0);
                if (bytes_read < 0) {
                    if (errno == EAGAIN || errno == EINTR) continue;
                    throw std::system_error(errno, std::generic_category(), "recv failed");
                }

                process_buffer(std::span<const uint8_t>(buffer.data(), static_cast<size_t>(bytes_read)));
            }
        }
    }

private:
    void process_buffer(std::span<const uint8_t> data) const {
        auto len = static_cast<int>(data.size());
        auto nlh = reinterpret_cast<const struct nlmsghdr*>(data.data());

        for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) break;
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                auto err = reinterpret_cast<const struct nlmsgerr*>(NLMSG_DATA(nlh));
                std::cerr << "Netlink error: " << err->error << "\n";
                continue;
            }

            if (nlh->nlmsg_type == RTM_NEWLINK || nlh->nlmsg_type == RTM_DELLINK) {
                handle_link_event(nlh);
            } else if (nlh->nlmsg_type == RTM_NEWADDR || nlh->nlmsg_type == RTM_DELADDR) {
                handle_addr_event(nlh);
            }
        }
    }

    void handle_link_event(const struct nlmsghdr* nlh) const {
        auto ifi = reinterpret_cast<const struct ifinfomsg*>(NLMSG_DATA(nlh));
        auto rta = IFLA_RTA(ifi);
        int rta_len = IFLA_PAYLOAD(nlh);
        std::string_view ifname = "unknown";

        for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
            if (rta->rta_type == IFLA_IFNAME) {
                ifname = std::string_view(reinterpret_cast<const char*>(RTA_DATA(rta)));
            }
        }

        std::string_view action = (nlh->nlmsg_type == RTM_NEWLINK) ? "NEWLINK" : "DELLINK";
        bool is_up = (ifi->ifi_flags & IFF_UP) != 0;
        bool is_running = (ifi->ifi_flags & IFF_RUNNING) != 0;

        std::cout << "[LINK " << action << "] Interface " << ifname 
                  << " (index " << ifi->ifi_index << "): State=" 
                  << (is_up ? "UP" : "DOWN") << ", Running=" 
                  << (is_running ? "YES" : "NO") << "\n";
    }

    void handle_addr_event(const struct nlmsghdr* nlh) const {
        auto ifa = reinterpret_cast<const struct ifaddrmsg*>(NLMSG_DATA(nlh));
        auto rta = IFA_RTA(ifa);
        int rta_len = IFA_PAYLOAD(nlh);
        char ip_buf[INET_ADDRSTRLEN] = "0.0.0.0";

        for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
            if (rta->rta_type == IFA_ADDRESS || rta->rta_type == IFA_LOCAL) {
                auto addr = reinterpret_cast<const struct in_addr*>(RTA_DATA(rta));
                ::inet_ntop(AF_INET, addr, ip_buf, sizeof(ip_buf));
            }
        }

        std::string_view action = (nlh->nlmsg_type == RTM_NEWADDR) ? "ADD_ADDR" : "DEL_ADDR";
        std::cout << "[ADDR " << action << "] Interface index " << ifa->ifa_index 
                  << ": IP " << ip_buf << "/" << static_cast<int>(ifa->ifa_prefixlen) << "\n";
    }
};

int main() {
    try {
        NetlinkMonitor monitor;
        monitor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
