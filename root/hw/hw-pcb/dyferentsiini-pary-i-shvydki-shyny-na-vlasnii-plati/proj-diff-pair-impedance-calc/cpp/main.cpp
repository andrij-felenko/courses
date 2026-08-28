#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <string_view>
#include <memory>
#include <expected>

namespace pcb::em {

constexpr double EPS_0 = 8.8541878128e-12;   // Ф / м
constexpr double MU_0  = 1.2566370614e-6;    // Гн / м
constexpr double C_LIGHT = 299792458.0;      // м / с

struct PcbGeometry {
    double w_mm{ 0.16 };       // Ширина провідника (мм)
    double s_mm{ 0.14 };       // Зазор між провідниками (мм)
    double t_mm{ 0.035 };      // Товщина фольги (мм)
    double h_mm{ 0.100 };      // Висота діелектрика до землі (мм)
    double er_sub{ 4.1 };      // Діелектрична проникність підкладки
    double t_mask_mm{ 0.020 }; // Товщина паяльної маски (мм)
    double er_mask{ 3.5 };     // Діелектрична проникність маски
    double g_coplanar_mm{ 0.0 }; // Зазор до бічної землі (0 якщо немає)
};

struct FieldAnalysisResult {
    double z_diff_ohm{ 0.0 };
    double z_comm_ohm{ 0.0 };
    double z_odd_ohm{ 0.0 };
    double z_even_ohm{ 0.0 };
    double c_odd_pf_m{ 0.0 };
    double c_even_pf_m{ 0.0 };
    double l_odd_nh_m{ 0.0 };
    double l_even_nh_m{ 0.0 };
    double er_eff_odd{ 0.0 };
    double er_eff_even{ 0.0 };
    double v_prop_odd_mm_ps{ 0.0 };
    double v_prop_even_mm_ps{ 0.0 };
    double fext_ps_m{ 0.0 };
};

enum class SolverError {
    InvalidGeometry,
    ConvergenceFailed,
    OutOfMemory
};

class FdmFieldSolver2D {
public:
    explicit FdmFieldSolver2D(int nx = 240, int ny = 160)
        : nx_{ nx }, ny_{ ny }, v_(nx * ny, 0.0), er_(nx * ny, 1.0), is_fixed_(nx * ny, false) {}

    [[nodiscard]] std::expected<FieldAnalysisResult, SolverError>
    solve(const PcbGeometry& geo) {
        if (geo.w_mm <= 0.0 || geo.s_mm <= 0.0 || geo.h_mm <= 0.0 || geo.er_sub < 1.0) {
            return std::unexpected(SolverError::InvalidGeometry);
        }

        const double total_width_mm = 6.0 * geo.h_mm + 2.0 * geo.w_mm + geo.s_mm;
        const double total_height_mm = 5.0 * geo.h_mm;

        dx_ = (total_width_mm * 1e-3) / (nx_ - 1);
        dy_ = (total_height_mm * 1e-3) / (ny_ - 1);

        const int gnd_j = 0;
        const int sub_top_j = static_cast<int>(std::round((geo.h_mm * 1e-3) / dy_));
        const int foil_top_j = sub_top_j + static_cast<int>(std::round((geo.t_mm * 1e-3) / dy_));
        const int mask_top_j = foil_top_j + static_cast<int>(std::round((geo.t_mask_mm * 1e-3) / dy_));

        const int mid_i = nx_ / 2;
        const int s_half_nodes = static_cast<int>(std::round(((geo.s_mm * 0.5) * 1e-3) / dx_));
        const int w_nodes = static_cast<int>(std::round((geo.w_mm * 1e-3) / dx_));

        const int trace1_x1 = mid_i - s_half_nodes - w_nodes;
        const int trace1_x2 = mid_i - s_half_nodes;
        const int trace2_x1 = mid_i + s_half_nodes;
        const int trace2_x2 = mid_i + s_half_nodes + w_nodes;

        const double mu = 0.5 * (std::cos(std::numbers::pi / nx_) + std::cos(std::numbers::pi / ny_));
        const double omega = 2.0 / (1.0 + std::sqrt(1.0 - mu * mu));

        double c_odd{ 0.0 }, c_odd_0{ 0.0 };
        double c_even{ 0.0 }, c_even_0{ 0.0 };

        for (int pass = 0; pass < 2; ++pass) {
            for (int mode = 0; mode < 2; ++mode) {
                reset_grid();

                for (int j = 0; j < ny_; ++j) {
                    for (int i = 0; i < nx_; ++i) {
                        if (pass == 0) {
                            if (j <= sub_top_j) {
                                er_[idx(i, j)] = geo.er_sub;
                            } else if (j <= mask_top_j && geo.t_mask_mm > 0.0) {
                                er_[idx(i, j)] = geo.er_mask;
                            } else {
                                er_[idx(i, j)] = 1.0;
                            }
                        } else {
                            er_[idx(i, j)] = 1.0;
                        }
                    }
                }

                for (int i = 0; i < nx_; ++i) {
                    const int c = idx(i, gnd_j);
                    v_[c] = 0.0;
                    is_fixed_[c] = true;
                }

                const double v1 = 1.0;
                const double v2 = (mode == 0) ? -1.0 : 1.0;

                for (int j = sub_top_j; j <= foil_top_j; ++j) {
                    for (int i = trace1_x1; i <= trace1_x2; ++i) {
                        const int c = idx(i, j);
                        v_[c] = v1;
                        is_fixed_[c] = true;
                    }
                    for (int i = trace2_x1; i <= trace2_x2; ++i) {
                        const int c = idx(i, j);
                        v_[c] = v2;
                        is_fixed_[c] = true;
                    }
                }

                for (int iter = 0; iter < 1200; ++iter) {
                    const double diff = iterate_sor(omega);
                    if (diff < 1e-6) break;
                }

                const int bx1 = std::max(1, trace1_x1 - 4);
                const int bx2 = trace1_x2 + 2;
                const int by1 = std::max(1, sub_top_j - 4);
                const int by2 = foil_top_j + 4;

                const double q = compute_charge(bx1, bx2, by1, by2);

                if (pass == 0 && mode == 0) c_odd = q / 1.0;
                if (pass == 0 && mode == 1) c_even = q / 1.0;
                if (pass == 1 && mode == 0) c_odd_0 = q / 1.0;
                if (pass == 1 && mode == 1) c_even_0 = q / 1.0;
            }
        }

        FieldAnalysisResult res;
        res.c_odd_pf_m = c_odd * 1e12;
        res.c_even_pf_m = c_even * 1e12;

        res.l_odd_nh_m = (1.0 / (C_LIGHT * C_LIGHT * c_odd_0)) * 1e9;
        res.l_even_nh_m = (1.0 / (C_LIGHT * C_LIGHT * c_even_0)) * 1e9;

        res.er_eff_odd = c_odd / c_odd_0;
        res.er_eff_even = c_even / c_even_0;

        res.z_odd_ohm = 1.0 / (C_LIGHT * std::sqrt(c_odd * c_odd_0));
        res.z_even_ohm = 1.0 / (C_LIGHT * std::sqrt(c_even * c_even_0));

        res.z_diff_ohm = 2.0 * res.z_odd_ohm;
        res.z_comm_ohm = 0.5 * res.z_even_ohm;

        res.v_prop_odd_mm_ps = (C_LIGHT / std::sqrt(res.er_eff_odd)) * 1e-9;
        res.v_prop_even_mm_ps = (C_LIGHT / std::sqrt(res.er_eff_even)) * 1e-9;

        const double t_odd_ps_m = (1.0 / (res.v_prop_odd_mm_ps * 1e9)) * 1e12;
        const double t_even_ps_m = (1.0 / (res.v_prop_even_mm_ps * 1e9)) * 1e12;
        res.fext_ps_m = std::abs(t_even_ps_m - t_odd_ps_m);

        return res;
    }

private:
    int nx_{ 0 };
    int ny_{ 0 };
    double dx_{ 0.0 };
    double dy_{ 0.0 };
    std::vector<double> v_;
    std::vector<double> er_;
    std::vector<bool> is_fixed_;

    [[nodiscard]] inline int idx(int i, int j) const noexcept {
        return j * nx_ + i;
    }

    void reset_grid() {
        std::fill(v_.begin(), v_.end(), 0.0);
        std::fill(is_fixed_.begin(), is_fixed_.end(), false);
    }

    double iterate_sor(double omega) {
        double max_diff{ 0.0 };
        for (int j = 1; j < ny_ - 1; ++j) {
            for (int i = 1; i < nx_ - 1; ++i) {
                const int c = idx(i, j);
                if (is_fixed_[c]) continue;

                const double er_c = er_[c];
                const double er_r = 0.5 * (er_c + er_[idx(i + 1, j)]);
                const double er_l = 0.5 * (er_c + er_[idx(i - 1, j)]);
                const double er_t = 0.5 * (er_c + er_[idx(i, j + 1)]);
                const double er_b = 0.5 * (er_c + er_[idx(i, j - 1)]);

                const double sum_er = er_r + er_l + er_t + er_b;
                const double v_gs = (er_r * v_[idx(i + 1, j)] +
                                     er_l * v_[idx(i - 1, j)] +
                                     er_t * v_[idx(i, j + 1)] +
                                     er_b * v_[idx(i, j - 1)]) / sum_er;

                const double v_new = (1.0 - omega) * v_[c] + omega * v_gs;
                const double diff = std::abs(v_new - v_[c]);
                if (diff > max_diff) max_diff = diff;
                v_[c] = v_new;
            }
        }
        return max_diff;
    }

    [[nodiscard]] double compute_charge(int x1, int x2, int y1, int y2) const {
        double total_q{ 0.0 };
        for (int i = x1; i <= x2; ++i) {
            const double er_b = 0.5 * (er_[idx(i, y1)] + er_[idx(i, y1 - 1)]);
            total_q += EPS_0 * er_b * ((v_[idx(i, y1)] - v_[idx(i, y1 - 1)]) / dy_) * dx_;

            const double er_t = 0.5 * (er_[idx(i, y2)] + er_[idx(i, y2 + 1)]);
            total_q += EPS_0 * er_t * ((v_[idx(i, y2)] - v_[idx(i, y2 + 1)]) / dy_) * dx_;
        }
        for (int j = y1; j <= y2; ++j) {
            const double er_l = 0.5 * (er_[idx(x1, j)] + er_[idx(x1 - 1, j)]);
            total_q += EPS_0 * er_l * ((v_[idx(x1, j)] - v_[idx(x1 - 1, j)]) / dx_) * dy_;

            const double er_r = 0.5 * (er_[idx(x2, j)] + er_[idx(x2 + 1, j)]);
            total_q += EPS_0 * er_r * ((v_[idx(x2, j)] - v_[idx(x2 + 1, j)]) / dx_) * dy_;
        }
        return total_q;
    }
};

class WadellAnalyticalModel {
public:
    [[nodiscard]] static FieldAnalysisResult solve(const PcbGeometry& geo) noexcept {
        FieldAnalysisResult res;
        const double w = geo.w_mm;
        const double h = geo.h_mm;
        const double t = geo.t_mm;
        const double s = geo.s_mm;
        const double er = geo.er_sub;

        const double dw = (t / std::numbers::pi) * (1.0 + std::log(2.0 * h / t));
        const double w_eff = w + dw;

        const double u = w_eff / h;
        const double er_eff = 0.5 * (er + 1.0) + 0.5 * (er - 1.0) * std::pow(1.0 + 12.0 / u, -0.5);
        const double z0 = (376.73 / std::sqrt(er_eff)) / (u + 1.393 + 0.667 * std::log(u + 1.444));

        res.z_diff_ohm = 2.0 * z0 * (1.0 - 0.48 * std::exp(-0.96 * (s / h)));
        res.z_comm_ohm = 0.5 * z0 * (1.0 + 0.86 * std::exp(-1.15 * (s / h)));

        if (geo.t_mask_mm > 0.0) {
            res.z_diff_ohm *= 0.965;
            res.z_comm_ohm *= 0.970;
        }

        res.z_odd_ohm = res.z_diff_ohm * 0.5;
        res.z_even_ohm = res.z_comm_ohm * 2.0;
        res.er_eff_odd = er_eff * 0.95;
        res.er_eff_even = er_eff * 1.05;

        res.v_prop_odd_mm_ps = (C_LIGHT / std::sqrt(res.er_eff_odd)) * 1e-9;
        res.v_prop_even_mm_ps = (C_LIGHT / std::sqrt(res.er_eff_even)) * 1e-9;

        return res;
    }
};

void print_report(std::string_view title, const PcbGeometry& geo, const FieldAnalysisResult& res) {
    std::cout << "=================================================================\n"
              << "  " << title << "\n"
              << "=================================================================\n"
              << std::fixed << std::setprecision(3)
              << " Геометрія: w=" << geo.w_mm << " мм, s=" << geo.s_mm << " мм, h=" 
              << geo.h_mm << " мм, t=" << geo.t_mm << " мм, er=" << std::setprecision(2) << geo.er_sub << "\n";
    if (geo.t_mask_mm > 0.0) {
        std::cout << " Маска    : t_mask=" << geo.t_mask_mm << " мм, er_mask=" << geo.er_mask << "\n";
    }
    std::cout << "-----------------------------------------------------------------\n"
              << std::setprecision(2)
              << " Диференційний імпеданс Z_diff : " << res.z_diff_ohm << " Ом\n"
              << " Синфазний імпеданс     Z_comm : " << res.z_comm_ohm << " Ом\n"
              << " Модальні опори (Odd / Even)   : " << res.z_odd_ohm << " Ом / " << res.z_even_ohm << " Ом\n"
              << " Погонна ємність C_odd         : " << res.c_odd_pf_m << " пФ/м (C_even = " << res.c_even_pf_m << " пФ/м)\n"
              << " Погонна індуктивність L_odd   : " << res.l_odd_nh_m << " нГн/м (L_even = " << res.l_even_nh_m << " нГн/м)\n"
              << std::setprecision(3)
              << " Ефективна діелектрична ε_eff  : Odd=" << res.er_eff_odd << ", Even=" << res.er_eff_even << "\n"
              << std::setprecision(4)
              << " Фазова швидкість v_prop       : Odd=" << res.v_prop_odd_mm_ps << " мм/пс, Even=" 
              << res.v_prop_even_mm_ps << " мм/пс\n";
    if (res.fext_ps_m > 0.0) {
        std::cout << std::setprecision(2) << " Фазовий перекіс FEXT          : " << res.fext_ps_m << " пс / метр\n";
    }
    std::cout << "=================================================================\n\n";
}

} // namespace pcb::em
