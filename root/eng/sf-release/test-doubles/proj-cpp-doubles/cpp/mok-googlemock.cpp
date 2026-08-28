#include <gmock/gmock.h>
#include <gtest/gtest.h>

using ::testing::_;
using ::testing::AnyNumber;
using ::testing::AtLeast;
using ::testing::ElementsAre;
using ::testing::NiceMock;
using ::testing::Return;
using ::testing::SizeIs;

class MockTransport : public ITransport {
 public:
  MOCK_METHOD(SendStatus,  send, (std::span<const std::uint8_t> chunk), (override));
  MOCK_METHOD(std::size_t, mtu,  (), (const, override));
};

TEST(UplinkVirtual, RetriesUntilTheQueueFrees) {
  NiceMock<MockTransport> t;
  ON_CALL(t, mtu()).WillByDefault(Return(std::size_t{64}));

  EXPECT_CALL(t, send(SizeIs(16)))
      .Times(3)
      .WillOnce(Return(SendStatus::WouldBlock))
      .WillOnce(Return(SendStatus::WouldBlock))
      .WillOnce(Return(SendStatus::Ok));

  Uplink<ITransport> up(t, /*max_retries=*/3);
  const std::vector<std::uint8_t> frame(16, 0x7E);

  EXPECT_EQ(up.sendFrame(frame), UplinkResult::Sent);
}
