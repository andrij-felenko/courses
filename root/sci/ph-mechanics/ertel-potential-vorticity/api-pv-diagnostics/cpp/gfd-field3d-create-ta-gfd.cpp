class Field3DOwner {
public:
    Field3DOwner(int nx, int ny, int nz)
        : nx_(nx), ny_(ny), nz_(nz), buffer_(static_cast<size_t>(nx) * ny * nz, 0.0) {}

    [[nodiscard]] std::span<double> span() noexcept { return buffer_; }
    [[nodiscard]] std::span<const double> span() const noexcept { return buffer_; }

private:
    int nx_, ny_, nz_;
    std::vector<double> buffer_;
};
