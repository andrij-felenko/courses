enum class BCType {
    Periodic = 0,
    Clamped  = 1,
    Neumann  = 2
};

struct PVOptions {
    bool use_pvu_units{true};
    int diff_order{2};
    BCType bc_x{BCType::Periodic};
    BCType bc_y{BCType::Neumann};
    BCType bc_z{BCType::Neumann};
};
