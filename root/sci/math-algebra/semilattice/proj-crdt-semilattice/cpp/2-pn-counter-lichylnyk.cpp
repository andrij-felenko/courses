class PNCounter {
public:
    explicit PNCounter(std::string node_id)
        : p_counter_(node_id), n_counter_(std::move(node_id)) {}

    void increment(uint64_t delta = 1) {
        p_counter_.increment(delta);
    }

    void decrement(uint64_t delta = 1) {
        n_counter_.increment(delta);
    }

    [[nodiscard]] int64_t value() const noexcept {
        return static_cast<int64_t>(p_counter_.value()) - 
               static_cast<int64_t>(n_counter_.value());
    }

    void merge(const PNCounter& other) {
        p_counter_.merge(other.p_counter_);
        n_counter_.merge(other.n_counter_);
    }

private:
    GCounter p_counter_;
    GCounter n_counter_;
};
