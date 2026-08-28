struct QuantifierDescriptor {
    QuantifierKind kind{QuantifierKind::Exists};
    std::string var_symbol;
    bool is_bounded{false};
    std::uint64_t bound_limit{0};
};

struct HierarchyAnalysisResult {
    ArithmeticClassType class_type{ArithmeticClassType::Delta0};
    std::uint32_t level_n{0};
    std::uint32_t oracle_jump_required{0};
    std::size_t raw_quantifier_count{0};
    std::size_t contracted_count{0};
    bool is_decidable{true};
    bool is_recursively_enumerable{true};
};
