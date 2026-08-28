// contract_udp_test.cpp — повільна смуга, нічний прогін
class UdpLoopbackTransport {
 public:
  UdpLoopbackTransport(std::size_t mtu, int fd) : mtu_(mtu), fd_(fd) {}
  UdpLoopbackTransport(const UdpLoopbackTransport&) = delete;   // дескриптор не копіюють
  ~UdpLoopbackTransport() { ::close(fd_); }

  std::size_t mtu() const { return mtu_; }

  SendStatus send(std::span<const std::uint8_t> chunk) {
    if (chunk.size() > mtu_) return SendStatus::Fatal;        // ТЕ САМЕ правило, що у фейка
    const ssize_t n = ::send(fd_, chunk.data(), chunk.size(), MSG_DONTWAIT);
    if (n == static_cast<ssize_t>(chunk.size()))              return SendStatus::Ok;
    if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK))   return SendStatus::WouldBlock;
    return SendStatus::Fatal;
  }

 private:
  std::size_t mtu_;
  int         fd_;
};

template <> struct TransportFactory<UdpLoopbackTransport> {
  static std::unique_ptr<UdpLoopbackTransport> make() {
    // сокет під'єднано на 127.0.0.1, SO_SNDBUF навмисно малий,
    // щоб буфер відправлення переповнювався за розумний час
    return std::make_unique<UdpLoopbackTransport>(64, makeLoopbackSocket(/*sndbuf=*/2048));
  }
};
INSTANTIATE_TYPED_TEST_SUITE_P(UdpLoopback, TransportContract,
                               ::testing::Types<UdpLoopbackTransport>);
