namespace natural {

class Analyzer {
public:
    explicit Analyzer(const Config& config);
    ~Analyzer() noexcept;

    // Встановлення таблиці істинності через std::span
    void set_truth_table(std::span<const uint8_t> table_bytes);

    // Запуск аналізу натуральності
    [[nodiscard]] Result analyze() const;
};

} // namespace natural
