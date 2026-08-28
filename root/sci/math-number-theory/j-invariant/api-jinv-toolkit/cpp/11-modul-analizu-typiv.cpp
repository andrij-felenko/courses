namespace jinv {
enum class ReductionType {
    Good = 0,
    MultiplicativeSplit,
    MultiplicativeNonSplit,
    Additive
};

[[nodiscard]] ReductionType analyze_reduction(const GeneralWeierstrassCurve& curve, int64_t p);
}
