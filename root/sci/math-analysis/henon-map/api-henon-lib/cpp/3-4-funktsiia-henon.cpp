// C++20: Клас henon::Map у <henon/map.hpp>

namespace henon {

class Map {
public:
    constexpr Map() noexcept : params_{1.4, 0.3} {}
    constexpr explicit Map(Params params) noexcept : params_(params) {}
    constexpr Map(double a, double b) noexcept : params_{a, b} {}

    [[nodiscard]] constexpr Params params() const noexcept { return params_; }
    constexpr void set_params(Params p) noexcept { params_ = p; }

    [[nodiscard]] constexpr Point step(Point pt) const noexcept {
        return Point{
            .x = 1.0 - params_.a * pt.x * pt.x + pt.y,
            .y = params_.b * pt.x
        };
    }

    [[nodiscard]] std::expected<Point, Status> inverse_step(Point next) const noexcept {
        if (std::abs(params_.b) < 1e-15) {
            return std::unexpected(Status::InvalidParam);
        }
        double x_prev = next.y / params_.b;
        double y_prev = next.x - 1.0 + params_.a * (next.y / params_.b) * (next.y / params_.b);
        return Point{.x = x_prev, .y = y_prev};
    }

    [[nodiscard]] std::expected<std::vector<Point>, Status> 
    orbit(Point start, std::size_t transient, std::size_t count) const {
        std::vector<Point> buf(count);
        henon_point_t c_start{start.x, start.y};
        henon_params_t c_params{params_.a, params_.b};
        henon_status_t st = henon_iterate_batch(c_start, c_params, transient, count, 
                                                reinterpret_cast<henon_point_t*>(buf.data()));
        if (st != HENON_OK) {
            return std::unexpected(static_cast<Status>(st));
        }
        return buf;
    }

    [[nodiscard]] std::expected<LyapunovResult, Status> 
    lyapunov(Point start, std::size_t transient, std::size_t steps) const {
        henon_lyapunov_t c_res{};
        henon_point_t c_start{start.x, start.y};
        henon_params_t c_params{params_.a, params_.b};
        henon_status_t st = henon_compute_lyapunov(c_start, c_params, transient, steps, &c_res);
        if (st != HENON_OK) {
            return std::unexpected(static_cast<Status>(st));
        }
        return LyapunovResult{
            .lambda_1 = c_res.lambda_1,
            .lambda_2 = c_res.lambda_2,
            .kaplan_yorke = c_res.kaplan_yorke,
            .converged = c_res.converged
        };
    }

    [[nodiscard]] FixedPoints fixed_points() const noexcept {
        henon_params_t c_params{params_.a, params_.b};
        henon_fixed_points_t c_fp = henon_find_fixed_points(c_params);
        return FixedPoints{
            .p1 = Point{c_fp.p1.x, c_fp.p1.y},
            .p2 = Point{c_fp.p2.x, c_fp.p2.y},
            .is_real = c_fp.is_real
        };
    }

private:
    Params params_;
};

} // namespace henon
