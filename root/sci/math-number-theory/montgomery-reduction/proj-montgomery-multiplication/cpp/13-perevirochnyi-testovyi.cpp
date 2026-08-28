int main() {
    constexpr uint64_t n = 1000000007ULL;
    auto ctx_opt = Montgomery64::create(n);
    if (!ctx_opt) {
        std::cerr << "Помилка ініціалізації!\n";
        return 1;
    }
    const auto& ctx = *ctx_opt;

    constexpr uint64_t a = 123456789ULL;
    constexpr uint64_t b = 987654321ULL;
    const uint64_t expected = static_cast<unsigned __int128>(a) * b % n;

    const uint64_t a_bar = ctx.to_domain(a);
    const uint64_t b_bar = ctx.to_domain(b);
    const uint64_t c_bar = ctx.multiply(a_bar, b_bar);
    const uint64_t actual = ctx.from_domain(c_bar);

    std::cout << "Множення: очікувано = " << expected << ", отримано = " << actual
              << " [" << (expected == actual ? "OK" : "FAIL") << "]\n";

    constexpr uint64_t exp = 65537ULL;
    const uint64_t res_pow = modular_pow(ctx, a, exp);
    std::cout << "Піднесення: " << a << "^" << exp << " mod " << n << " = " << res_pow << "\n";

    const std::vector<uint64_t> vals = {123, 456, 789};
    const auto invs = batch_invert(ctx, vals);
    for (size_t i = 0; i < vals.size(); ++i) {
        const uint64_t check = static_cast<unsigned __int128>(vals[i]) * invs[i] % n;
        std::cout << "Обернення: " << vals[i] << "^-1 mod " << n
                  << " = " << invs[i] << " (перевірка = " << check << ")\n";
    }

    return 0;
}
