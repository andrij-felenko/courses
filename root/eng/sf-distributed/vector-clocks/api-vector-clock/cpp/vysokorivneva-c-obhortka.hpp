namespace vclock {

class VectorClockHandle {
public:
    explicit VectorClockHandle(size_t initial_capacity = 8);
    VectorClockHandle(std::initializer_list<std::pair<vc_node_id_t, vc_counter_t>> init);

    // RAII та заборона неявного копіювання важких ресурсів
    ~VectorClockHandle();
    VectorClockHandle(const VectorClockHandle& other);
    VectorClockHandle& operator=(const VectorClockHandle& other);
    VectorClockHandle(VectorClockHandle&& other) noexcept;
    VectorClockHandle& operator=(VectorClockHandle&& other) noexcept;

    // Основні операції
    void tick(vc_node_id_t node_id);
    void set(vc_node_id_t node_id, vc_counter_t counter);
    [[nodiscard]] vc_counter_t get(vc_node_id_t node_id) const noexcept;
    void merge(const VectorClockHandle& other);
    void prune(size_t max_entries);

    // Порівняння та перевірка причинності
    [[nodiscard]] VectorComparison compare(const VectorClockHandle& other) const noexcept;
    [[nodiscard]] bool dominates(const VectorClockHandle& other) const noexcept;
    [[nodiscard]] bool is_concurrent_with(const VectorClockHandle& other) const noexcept;

    // Серіалізація
    [[nodiscard]] std::vector<uint8_t> to_binary() const;
    static std::expected<VectorClockHandle, vc_status_t> from_binary(std::span<const uint8_t> data);
    [[nodiscard]] std::string to_json() const;

private:
    vc_dynamic_clock_t raw_;
};

} // namespace vclock
