#include <numeric>

TEST(UplinkStatic, DeliversWholeFrameInPieces) {
  FakeTransport t(/*mtu=*/8, /*capacity=*/16);
  Uplink up(t);

  std::vector<std::uint8_t> frame(20);
  std::iota(frame.begin(), frame.end(), std::uint8_t{1});

  ASSERT_EQ(up.sendFrame(frame), UplinkResult::Sent);
  ASSERT_EQ(t.queued(), 3u);                          // 8 + 8 + 4

  std::vector<std::uint8_t> glued;
  while (t.queued() > 0) {
    const auto part = t.drainOne();
    glued.insert(glued.end(), part.begin(), part.end());
  }
  EXPECT_EQ(glued, frame);          // головна вимога: склеєне назад = вихідне
}

TEST(UplinkStatic, ReportsCongestionWhenNobodyDrains) {
  FakeTransport t(/*mtu=*/64, /*capacity=*/2);
  Uplink up(t, /*max_retries=*/3);

  const std::vector<std::uint8_t> frame(64 * 5, 0x11);   // п'ять шматків у чергу на два

  EXPECT_EQ(up.sendFrame(frame), UplinkResult::Congested);
  EXPECT_EQ(t.queued(), 2u);        // прийнято рівно стільки, скільки влізло
}
