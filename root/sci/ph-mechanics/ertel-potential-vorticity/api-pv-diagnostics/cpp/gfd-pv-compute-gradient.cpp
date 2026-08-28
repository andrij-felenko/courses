struct GradientVectorResult {
    std::vector<double> dx;
    std::vector<double> dy;
    std::vector<double> dz;
};

[[nodiscard]] std::expected<GradientVectorResult, gfd_status_t> computeGradient(
    const Grid& grid,
    Field3DView scalar
);
