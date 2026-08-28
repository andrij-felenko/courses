template <size_t Capacity>
class GoalEngine {
public:
    explicit GoalEngine(void* context = nullptr) noexcept;
    bool push(const Goal& goal) noexcept;
    std::optional<Goal> fetch_next() noexcept;
    void step(uint32_t now_ms, EventQueue<16>& out_queue) noexcept;
    void complete_active() noexcept;
    void abort_all() noexcept;
    [[nodiscard]] bool has_active() const noexcept;
    [[nodiscard]] const std::optional<Goal>& active() const noexcept;

private:
    std::array<Goal, Capacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    std::optional<Goal> active_goal_{std::nullopt};
    void* context_{nullptr};
};
