namespace jinv {
struct PolynomialFp2 {
    std::vector<FieldElement2> coeffs;
};

[[nodiscard]] std::vector<FieldElement2> find_roots(
    const PolynomialFp2& poly,
    int64_t p
);
}
