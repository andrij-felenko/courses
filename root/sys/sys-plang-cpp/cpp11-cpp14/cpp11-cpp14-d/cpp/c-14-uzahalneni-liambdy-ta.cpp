// C++14 узагальнена лямбда
auto print_pair = [](const auto& first, const auto& second) {
    std::cout << first << " : " << second << "\n";
};

// Еквівалентний клас, згенерований компілятором:
struct __CompilerGeneratedLambda {
    template<typename T1, typename T2>
    auto operator()(const T1& first, const T2& second) const {
        std::cout << first << " : " << second << "\n";
    }
};
