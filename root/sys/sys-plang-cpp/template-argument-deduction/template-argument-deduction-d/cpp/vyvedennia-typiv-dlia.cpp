auto multiplier = [](auto a, auto b) {
    return a * b;
};

// Еквівалентний клас, згенерований компілятором:
struct __LambdaMultiplier {
    template<typename T1, typename T2>
    auto operator()(T1 a, T2 b) const {
        return a * b;
    }
};
