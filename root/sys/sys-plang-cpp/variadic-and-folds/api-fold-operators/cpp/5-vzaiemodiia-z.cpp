namespace math {
    struct Vector3D {
        double x, y, z;
    };

    Vector3D operator+(const Vector3D& a, const Vector3D& b) noexcept {
        return { a.x + b.x, a.y + b.y, a.z + b.z };
    }
}

template <typename... Vectors>
auto sum_vectors(const Vectors&... vecs) {
    // Вираз згортки автоматично знаходить math::operator+ через ADL
    return (... + vecs);
}
