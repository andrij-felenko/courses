struct ExperimentConfig {
    double sampling_rate{0.10};       // 10% семплювання
    double epsilon{1e-6};              // Точність порівняння
    uint32_t timeout_ms{50};           // Жорсткий ліміт виконання
    bool is_enabled{true};             // Головний перемикач
};

class DynamicConfigManager {
public:
    void update_config(ExperimentConfig new_cfg) {
        auto new_ptr = std::make_shared<const ExperimentConfig>(new_cfg);
        std::atomic_store(&active_config_, new_ptr);
    }

    [[nodiscard]] std::shared_ptr<const ExperimentConfig> get() const noexcept {
        return std::atomic_load(&active_config_);
    }

private:
    std::shared_ptr<const ExperimentConfig> active_config_{
        std::make_shared<const ExperimentConfig>()
    };
};
