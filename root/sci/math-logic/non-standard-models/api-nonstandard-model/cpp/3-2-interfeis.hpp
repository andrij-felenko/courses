namespace NonStandard {

class NonStandardTuringMachine {
public:
    explicit NonStandardTuringMachine(size_t tape_size = 64);

    void step();
    void execute_hyper_steps(const NonStandardInt& hyper_limit);

    [[nodiscard]] std::string get_status() const;
    [[nodiscard]] const std::vector<uint8_t>& get_tape() const noexcept;
    [[nodiscard]] const NonStandardInt& get_step_count() const noexcept;
    [[nodiscard]] bool is_halted() const noexcept;
};

} // namespace NonStandard
