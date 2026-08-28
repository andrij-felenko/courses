  class MemoryLeakDetectorFixture : public ::testing::Test {
      MemoryTracker::Stats initial_stats_;
  protected:
      void SetUp() override { initial_stats_ = MemoryTracker::get_stats(); }
      void TearDown() override {
          auto current = MemoryTracker::get_stats();
          EXPECT_EQ(current.current_active_bytes, initial_stats_.current_active_bytes) << "Тест допустив витік пам'яті!";
          EXPECT_EQ(current.mismatch_errors_count, initial_stats_.mismatch_errors_count) << "Виявлено невідповідність new/delete!";
      }
  };
