namespace cpp {

class DovetailEngine {
private:
    EnumeratorHandle* handle_{nullptr};

public:
    explicit DovetailEngine(const DovetailConfig& config = {}) {
        if (enumerator_create(&config, &handle_) != ENUM_OK) {
            throw std::bad_alloc();
        }
    }

    ~DovetailEngine() {
        if (handle_) {
            enumerator_destroy(handle_);
        }
    }

    // Заборона копіювання (RAII семантика)
    DovetailEngine(const DovetailEngine&) = delete;
    DovetailEngine& operator=(const DovetailEngine&) = delete;

    // Дозвіл переміщення
    DovetailEngine(DovetailEngine&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    void register_task(TaskStepFunc step_fn, void* ctx) {
        uint32_t id = 0;
        auto status = enumerator_register_task(handle_, step_fn, ctx, &id);
        if (status != ENUM_OK) {
            throw std::runtime_error("Task registration failed");
        }
    }

    void step_diagonal() {
        if (enumerator_step_diagonal(handle_, nullptr) != ENUM_OK) {
            throw std::runtime_error("Diagonal step execution failed");
        }
    }

    [[nodiscard]] std::span<const int32_t> results() const {
        const int32_t* arr = nullptr;
        size_t count = 0;
        enumerator_get_results(handle_, &arr, &count);
        return {arr, count};
    }
};

} // namespace cpp
