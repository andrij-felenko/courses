struct QueryEntry {
    uint64_t query_value;
    bool answer;
    uint64_t step_timestamp;
};

struct QueryTrace {
    std::vector<QueryEntry> entries;
    uint64_t max_queried_value{0};

    [[nodiscard]] uint64_t get_use_bound() const noexcept {
        return entries.empty() ? 0 : max_queried_value + 1;
    }
};

class IOracleProvider {
public:
    virtual ~IOracleProvider() = default;
    [[nodiscard]] virtual bool contains(uint64_t value) const = 0;
    [[nodiscard]] virtual std::string_view get_type_name() const noexcept = 0;
};
