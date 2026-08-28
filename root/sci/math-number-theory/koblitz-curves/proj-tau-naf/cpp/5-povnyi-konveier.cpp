namespace koblitz {

/* Геометричне додавання точок кривої в координатах Лопеса-Дахаба */
ProjectivePoint point_add(const ProjectivePoint& p, const ProjectivePoint& q) noexcept;

/* Обчислення скалярного множення без жодного подвоєння точки */
[[nodiscard]] ProjectivePoint scalar_mul_tnaf(const ProjectivePoint& base, ZTauElement rho, int8_t mu) {
    const std::vector<int8_t> tnaf = generate_tnaf(rho, mu);
    const ProjectivePoint neg_base = point_negate(base);

    ProjectivePoint acc = ProjectivePoint::infinity();

    for (size_t i = tnaf.size(); i > 0; --i) {
        const size_t idx = i - 1;
        
        /* Автоморфізм Фробеніуса замість операції подвоєння */
        acc = frobenius(acc);

        if (tnaf[idx] == 1) {
            acc = point_add(acc, base);
        } else if (tnaf[idx] == -1) {
            acc = point_add(acc, neg_base);
        }
    }

    return acc;
}

} // namespace koblitz
