namespace gfd {

class PVDiagnosticEngine {
public:
    explicit PVDiagnosticEngine(gfd_grid_t grid, gfd_pv_options_t options = {})
        : grid_(grid), opts_(options) {}

    ~PVDiagnosticEngine() = default;

    PVDiagnosticEngine(const PVDiagnosticEngine&) = delete;
    PVDiagnosticEngine& operator=(const PVDiagnosticEngine&) = delete;
    PVDiagnosticEngine(PVDiagnosticEngine&&) noexcept = default;
    PVDiagnosticEngine& operator=(PVDiagnosticEngine&&) noexcept = default;

    [[nodiscard]] std::expected<std::vector<double>, gfd_status_t> execute(
        std::span<const double> u,
        std::span<const double> v,
        std::span<const double> w,
        std::span<const double> theta,
        std::span<const double> rho
    ) const {
        const size_t total_size = static_cast<size_t>(grid_.nx) * grid_.ny * grid_.nz;
        if (u.size() != total_size || v.size() != total_size ||
            w.size() != total_size || theta.size() != total_size ||
            rho.size() != total_size) 
        {
            return std::unexpected(GFD_ERR_SPAN_MISMATCH);
        }

        std::vector<double> pv_result(total_size, 0.0);

        gfd_field3d_t f_u{const_cast<double*>(u.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_v{const_cast<double*>(v.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_w{const_cast<double*>(w.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_th{const_cast<double*>(theta.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_rho{const_cast<double*>(rho.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_pv{pv_result.data(), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};

        gfd_status_t st = gfd_pv_compute_ertel(&grid_, &f_u, &f_v, &f_w, &f_th, &f_rho, &opts_, &f_pv);
        if (st != GFD_SUCCESS) {
            return std::unexpected(st);
        }

        return pv_result;
    }

private:
    gfd_grid_t grid_;
    gfd_pv_options_t opts_;
};

} // namespace gfd
