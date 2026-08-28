   // Приклад параметризованого тесту Google Test у C++
   class PaymentGatewayTest : public ::testing::TestWithParam<bool> {};

   TEST_P(PaymentGatewayTest, ProcessesCorrectlyInBothModes) {
       bool flag_state = GetParam();
       auto engine = create_mock_engine("payment-v2", flag_state);
       OrderProcessor processor(engine);
       EXPECT_TRUE(processor.checkout(100.0));
   }
   INSTANTIATE_TEST_SUITE_P(FlagStates, PaymentGatewayTest, ::testing::Values(true, false));
