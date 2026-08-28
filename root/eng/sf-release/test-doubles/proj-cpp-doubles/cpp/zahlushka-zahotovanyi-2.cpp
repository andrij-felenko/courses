struct StubTransport {                                // жодної бази, жодного virtual
  std::vector<SendStatus> script;
  std::size_t             next = 0;
  std::size_t             mtu_ = 64;

  SendStatus send(std::span<const std::uint8_t>) {
    return next < script.size() ? script[next++] : SendStatus::Ok;
  }
  std::size_t mtu() const { return mtu_; }
};

TEST(UplinkStatic, GivesUpAfterRetryBudget) {
  StubTransport t;
  t.script = {SendStatus::WouldBlock, SendStatus::WouldBlock,
              SendStatus::WouldBlock, SendStatus::WouldBlock};

  Uplink up(t, /*max_retries=*/3);                    // виведення: Uplink<StubTransport>
  const std::vector<std::uint8_t> frame(10, 0x55);

  EXPECT_EQ(up.sendFrame(frame), UplinkResult::Congested);
}
