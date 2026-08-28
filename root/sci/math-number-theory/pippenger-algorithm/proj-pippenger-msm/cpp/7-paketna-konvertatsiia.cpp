namespace msm {

/* Пакетне обернення масиву елементів поля за методом Монтгомері */
std::vector<FieldElement> batch_invert(std::span<const FieldElement> inputs) {
    const size_t count = inputs.size();
    if (count == 0) return {};

    std::vector<FieldElement> prefix_prod;
    prefix_prod.reserve(count);

    FieldElement cur = inputs[0];
    prefix_prod.push_back(cur);

    for (size_t i = 1; i < count; ++i) {
        cur = mul(cur, inputs[i]);
        prefix_prod.push_back(cur);
    }

    /* Єдина польова інверсія для спільного добутку */
    FieldElement all_inv = inv(prefix_prod.back());

    std::vector<FieldElement> inverses(count);
    for (size_t i = count - 1; i > 0; --i) {
        inverses[i] = mul(all_inv, prefix_prod[i - 1]);
        all_inv = mul(all_inv, inputs[i]);
    }
    inverses[0] = all_inv;

    return inverses;
}

} // namespace msm
