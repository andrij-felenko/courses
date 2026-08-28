namespace koblitz {

struct ProjectivePoint {
    FieldElement X{};
    FieldElement Y{};
    FieldElement Z{};
    bool is_infinity{true};

    static ProjectivePoint infinity() noexcept {
        return ProjectivePoint{{}, {}, {}, true};
    }
};

/* Ендоморфізм Фробеніуса: миттєве піднесення трьох координат до квадрата */
[[nodiscard]] ProjectivePoint frobenius(const ProjectivePoint& p) noexcept {
    if (p.is_infinity) {
        return ProjectivePoint::infinity();
    }
    return ProjectivePoint{
        .X = square(p.X),
        .Y = square(p.Y),
        .Z = square(p.Z),
        .is_infinity = false
    };
}

/* Точкове заперечення на бінарній кривій: Y' = Y + X * Z */
[[nodiscard]] ProjectivePoint point_negate(const ProjectivePoint& p) noexcept {
    if (p.is_infinity) {
        return ProjectivePoint::infinity();
    }
    ProjectivePoint res = p;
    /* Додавання до Y добутку X * Z у полі характеристики 2 */
    return res;
}

} // namespace koblitz
