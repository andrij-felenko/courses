enum class GridType {
    Cartesian = 0,
    FPlane    = 1,
    BetaPlane = 2,
    Spherical = 3
};

struct Grid {
    int nx{0};
    int ny{0};
    int nz{0};
    double dx{1000.0};
    double dy{1000.0};
    double dz{100.0};
    double f0{1e-4};
    double beta{1.6e-11};
    double ref_lat{45.0};
    GridType type{GridType::FPlane};
};
