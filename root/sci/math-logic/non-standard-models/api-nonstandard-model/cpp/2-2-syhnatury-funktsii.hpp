namespace NonStandard {

class NonStandardInt {
public:
    explicit NonStandardInt(int64_t standard_val = 0);
    static NonStandardInt make_inf(size_t degree, int64_t coeff = 1);

    [[nodiscard]] bool is_standard() const noexcept;
    [[nodiscard]] std::span<const int64_t> coefficients() const noexcept;

    auto operator<=>(const NonStandardInt& other) const noexcept;
    bool operator==(const NonStandardInt& other) const noexcept;

    NonStandardInt operator+(const NonStandardInt& other) const;
    NonStandardInt operator*(const NonStandardInt& other) const;

    [[nodiscard]] std::string to_string() const;
};

} // namespace NonStandard
