// Ідіоматична C++ RAII-обгортка із генерацією виключення std::system_error
namespace net {
    class NetlinkSocket {
    public:
        NetlinkSocket() {
            fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
            if (fd_ < 0) {
                throw std::system_error(errno, std::generic_category(), "Не вдалося створити сокет Netlink");
            }
        }
        ~NetlinkSocket() { if (fd_ >= 0) ::close(fd_); }
        [[nodiscard]] int native_handle() const noexcept { return fd_; }
    private:
        int fd_{-1};
    };
}
