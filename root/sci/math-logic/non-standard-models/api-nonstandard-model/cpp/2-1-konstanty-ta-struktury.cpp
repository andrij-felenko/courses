namespace NonStandard {

constexpr size_t MAX_DEGREE = 4;
constexpr size_t TAPE_SIZE = 64;

class NonStandardInt {
private:
    std::vector<int64_t> coeffs_;
};

class NonStandardTuringMachine {
private:
    std::vector<uint8_t> tape_;
    size_t head_pos_;
    int state_;
    NonStandardInt steps_;
    bool halted_;
};

} // namespace NonStandard
