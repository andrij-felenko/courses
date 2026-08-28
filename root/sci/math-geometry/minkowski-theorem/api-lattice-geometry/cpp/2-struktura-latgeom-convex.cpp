namespace latgeom {

enum class BodyType {
    Ellipsoid = 1,
    Hypercube = 2,
    CrossPolytope = 3
};

struct ConvexBody {
    size_t dimension{0};
    BodyType type{BodyType::Ellipsoid};
    std::vector<double> shape_matrix;
    std::vector<double> limits;
    double radius{0.0};
    double volume{0.0};
};

} // namespace latgeom
