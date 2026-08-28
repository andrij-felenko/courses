namespace fgh {

class Ordinal {
public:
    static OrdinalPtr make_zero();
    static OrdinalPtr make_finite(uint64_t val);
    static OrdinalPtr make_term(OrdinalPtr exp, uint64_t coeff, OrdinalPtr tail = nullptr);

    OrdinalPtr clone() const;
    bool is_limit() const;
    OrdinalPtr fundamental_sequence(uint64_t n) const;
};

class Evaluator {
public:
    explicit Evaluator(uint64_t max_steps = 1000000);
    
    uint64_t eval(const OrdinalNode* alpha, uint64_t n, EvalStats& stats);
};

} // namespace fgh
