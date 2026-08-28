#include <vector>
#include <span>

// Пакетне модульне обернення масиву чисел
[[nodiscard]] std::vector<uint64_t> batch_invert(const Montgomery64& ctx,
                                                 std::span<const uint64_t> inputs) {
    const size_t k = inputs.size();
    if (k == 0) return {};
    if (k == 1) {
        return {modular_pow(ctx, inputs[0], ctx.modulus() - 2)};
    }

    std::vector<uint64_t> in_bar(k);
    std::vector<uint64_t> prod(k);
    for (size_t i = 0; i < k; ++i) {
        in_bar[i] = ctx.to_domain(inputs[i]);
    }

    prod[0] = in_bar[0];
    for (size_t i = 1; i < k; ++i) {
        prod[i] = ctx.multiply(prod[i - 1], in_bar[i]);
    }

    const uint64_t full_prod = ctx.from_domain(prod[k - 1]);
    uint64_t inv = ctx.to_domain(modular_pow(ctx, full_prod, ctx.modulus() - 2));

    std::vector<uint64_t> out(k);
    for (size_t i = k - 1; i > 0; --i) {
        out[i] = ctx.from_domain(ctx.multiply(inv, prod[i - 1]));
        inv = ctx.multiply(inv, in_bar[i]);
    }
    out[0] = ctx.from_domain(inv);
    return out;
}
