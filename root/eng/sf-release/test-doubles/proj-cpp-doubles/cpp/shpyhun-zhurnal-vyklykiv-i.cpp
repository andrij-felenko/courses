class SpyTransport {
 public:
  struct Call { std::vector<std::uint8_t> chunk; SendStatus answered; };

  std::vector<Call>       calls;
  std::vector<SendStatus> script;      // шпигун уміє й заглушати
  std::size_t             mtu_ = 8;

  std::size_t mtu() const { return mtu_; }

  SendStatus send(std::span<const std::uint8_t> chunk) {
    const SendStatus st =
        calls.size() < script.size() ? script[calls.size()] : SendStatus::Ok;
    calls.push_back({{chunk.begin(), chunk.end()}, st});
    return st;
  }
};

TEST(UplinkStatic, RetryResendsTheSameChunk) {
  SpyTransport t;
  t.script = {SendStatus::WouldBlock};      // перша спроба відбита, далі все гаразд

  std::vector<std::uint8_t> frame(12);
  std::iota(frame.begin(), frame.end(), std::uint8_t{1});

  Uplink up(t);
  ASSERT_EQ(up.sendFrame(frame), UplinkResult::Sent);

  ASSERT_GE(t.calls.size(), 2u);
  EXPECT_EQ(t.calls[0].chunk, t.calls[1].chunk)
      << "після WouldBlock вузол з'їхав уперед і загубив шматок";
}
