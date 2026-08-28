namespace msm {

/* Неблокуюча черга завдань обчислення MSM */
class AsyncQueue {
public:
    explicit AsyncQueue(uint32_t num_workers = std::thread::hardware_concurrency());
    ~AsyncQueue();

    AsyncQueue(const AsyncQueue&) = delete;
    AsyncQueue& operator=(const AsyncQueue&) = delete;

    AsyncQueue(AsyncQueue&&) noexcept = default;
    AsyncQueue& operator=(AsyncQueue&&) noexcept = default;

    /**
     * Відправка асинхронного завдання, що повертає std::future.
     */
    [[nodiscard]] std::future<std::expected<PointJacobian, Status>> submit(
        std::span<const PointAffine> points,
        std::span<const FieldElement256> scalars,
        Config config = Config{}
    );

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msm
