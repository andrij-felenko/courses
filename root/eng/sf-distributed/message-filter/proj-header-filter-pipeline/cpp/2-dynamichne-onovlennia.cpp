class ThreadSafeFilterEngine {
public:
    FilterDecision process(const Message& msg) const {
        // Читачі отримують копію атомарного shared_ptr без жодних блокувань
        std::shared_ptr<const FilterPipeline> current = std::atomic_load(&pipeline_);
        return current->process(msg);
    }

    void update_rules(std::shared_ptr<const FilterPipeline> new_pipeline) {
        // Потік управління атомарно підміняє старий конвеєр новим
        std::atomic_store(&pipeline_, std::move(new_pipeline));
        // Старий конвеєр буде автоматично видалений, щойно його дочитає останній робочий потік
    }

private:
    std::shared_ptr<const FilterPipeline> pipeline_;
};
