// Тест ідемпотентності кодека на базі фреймворку Google Test
TEST(CodecGenerationLossTest, IdempotencyOnFixedGrid) {
    constexpr double QUANT_STEP = 0.05;
    constexpr size_t SAMPLES = 1000;
    
    GenerationSimulator sim(SAMPLES, 5.0, QUANT_STEP);
    
    auto step1 = sim.step(0.0); // 1-ше покоління
    auto step2 = sim.step(0.0); // 2-ге покоління
    
    // Перевірка: SNR другого покоління має збігатися з першим з точністю 1e-5
    EXPECT_NEAR(step1.snr_aligned, step2.snr_aligned, 1e-5);
}
