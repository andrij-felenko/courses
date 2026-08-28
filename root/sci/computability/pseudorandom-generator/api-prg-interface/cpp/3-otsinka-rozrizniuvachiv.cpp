struct TestResult {
    double prob_prg{0.0};
    double prob_random{0.0};
    double advantage{0.0};
    std::size_t total_samples{0};
};

std::expected<TestResult, nw_status_t> evaluateDistinguisher(
    const GeneratorContext& ctx,
    const Distinguisher& distinguisher,
    std::size_t num_samples
);
