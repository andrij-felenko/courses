struct BaroclinicGridConfig {
    size_t nx{0};
    size_t ny{0};
    size_t nz{0};
    double dx{10000.0};
    double dy{10000.0};
    double dz{100.0};
    double latitude_deg{45.0};
    double coriolis_f0{0.0};
    double gravity_g{9.80665};
    BaroclinicCoordType coord{BaroclinicCoordType::ZLevels};
    BaroclinicBcType bc{BaroclinicBcType::ZeroFill};
    BaroclinicFdOrder fd_order{BaroclinicFdOrder::Order2Central};
};
