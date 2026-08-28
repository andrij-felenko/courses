namespace otm {

template <typename T>
concept OracleProviderConcept = requires(T a, uint64_t val) {
    { a.contains(val) } -> std::same_as<bool>;
    { a.get_type_name() } -> std::convertible_to<std::string_view>;
};

struct ExecutionMetrics {
    uint64_t total_steps{0};
    uint64_t oracle_queries_count{0};
    uint64_t max_restraint_use{0};
    bool halted{false};
};

class MemoryBoundOracle final : public IOracleProvider {
private:
    std::vector<uint64_t> sorted_elements_;

public:
    explicit MemoryBoundOracle(std::vector<uint64_t> elements);
    [[nodiscard]] bool contains(uint64_t value) const override;
    [[nodiscard]] std::string_view get_type_name() const noexcept override {
        return "MemoryBoundOracle";
    }
};

class ExecutionEngine {
private:
    std::shared_ptr<IOracleProvider> oracle_;
    ExecutionMetrics metrics_;

public:
    explicit ExecutionEngine(std::shared_ptr<IOracleProvider> oracle)
        : oracle_(std::move(oracle)) {}

    [[nodiscard]] std::expected<ExecutionMetrics, otm_status_t>
    execute_machine(uint64_t machine_index, uint64_t input_x, uint64_t max_steps);
};

} // namespace otm
