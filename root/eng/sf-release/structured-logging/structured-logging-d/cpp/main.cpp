TEST(OrderServiceTest, EmitsStructuredLogOnPaymentFailure) {
    MemoryLogSink sink;
    OrderService service(sink);

    service.ProcessOrder(OrderParams{.id = 19482, .should_fail = true});

    ASSERT_EQ(sink.Events().size(), 1);
    const auto& log = sink.Events()[0];

    EXPECT_EQ(log.Get("msg"), "payment_failed");
    EXPECT_EQ(log.Get("order_id"), 19482);
    EXPECT_TRUE(log.Has("trace_id"));
    EXPECT_EQ(log.Get("level"), "ERROR");
}
