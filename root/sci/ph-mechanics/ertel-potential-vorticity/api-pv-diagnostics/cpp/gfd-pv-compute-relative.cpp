struct VorticityVectorResult {
    std::vector<double> wx;
    std::vector<double> wy;
    std::vector<double> wz;
};

[[nodiscard]] std::expected<VorticityVectorResult, gfd_status_t> computeRelativeVorticity(
    const Grid& grid,
    Field3DView u, Field3DView v, Field3DView w
);
