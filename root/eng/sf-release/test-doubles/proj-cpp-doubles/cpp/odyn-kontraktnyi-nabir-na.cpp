// transport_contract.h — набір, який компілюється для будь-якої реалізації
template <class T> struct TransportFactory;   // спеціалізуй під кожну реалізацію

template <class T>
class TransportContract : public testing::Test {};

TYPED_TEST_SUITE_P(TransportContract);

TYPED_TEST_P(TransportContract, MtuIsPositive) {
  auto t = TransportFactory<TypeParam>::make();
  EXPECT_GT(t->mtu(), 0u);
}

TYPED_TEST_P(TransportContract, AcceptsChunkOfExactlyMtu) {
  auto t = TransportFactory<TypeParam>::make();
  const std::vector<std::uint8_t> chunk(t->mtu(), 0xA5);
  EXPECT_EQ(t->send(chunk), SendStatus::Ok);
}

TYPED_TEST_P(TransportContract, RejectsChunkLargerThanMtu) {
  auto t = TransportFactory<TypeParam>::make();
  const std::vector<std::uint8_t> big(t->mtu() + 1, 0xA5);
  EXPECT_EQ(t->send(big), SendStatus::Fatal);
}

TYPED_TEST_P(TransportContract, EventuallyRefusesWhenNobodyDrains) {
  auto t = TransportFactory<TypeParam>::make();
  const std::vector<std::uint8_t> chunk(t->mtu(), 0xA5);

  bool refused = false;
  for (int i = 0; i < 100000 && !refused; ++i) {
    const SendStatus st = t->send(chunk);
    ASSERT_NE(st, SendStatus::Fatal) << "зламався замість того, щоб відмовити, на i=" << i;
    refused = (st == SendStatus::WouldBlock);
  }
  EXPECT_TRUE(refused) << "приймає без кінця — вузол ніколи не побачить затору";
}

REGISTER_TYPED_TEST_SUITE_P(TransportContract,
                            MtuIsPositive, AcceptsChunkOfExactlyMtu,
                            RejectsChunkLargerThanMtu, EventuallyRefusesWhenNobodyDrains);
