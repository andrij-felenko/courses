#include <vector>

struct StubTransport final : ITransport {             // під шов через ITransport
  std::vector<SendStatus> script;      // по одній відповіді на виклик
  std::size_t             next = 0;
  std::size_t             mtu_ = 64;

  SendStatus send(std::span<const std::uint8_t>) override {
    return next < script.size() ? script[next++] : SendStatus::Ok;
  }
  std::size_t mtu() const override { return mtu_; }
};

TEST(UplinkVirtual, GivesUpAfterRetryBudget) {
  StubTransport t;
  t.script = {SendStatus::WouldBlock, SendStatus::WouldBlock,
              SendStatus::WouldBlock, SendStatus::WouldBlock};

  Uplink<ITransport> up(t, /*max_retries=*/3);
  const std::vector<std::uint8_t> frame(10, 0x55);

  EXPECT_EQ(up.sendFrame(frame), UplinkResult::Congested);
}
