namespace latgeom {

struct BasisDescriptor {
    size_t dimension{0};
    std::vector<int64_t> basis_matrix;
    std::vector<double> gram_schmidt_basis;
    std::vector<double> mu_coefficients;
    std::vector<double> square_norms;
    double determinant{1.0};
    double log_determinant{0.0};
    double minkowski_radius{0.0};
    double gaussian_heuristic{0.0};
    double orthogonality_defect{1.0};
    bool is_orthogonalized{false};
};

} // namespace latgeom
