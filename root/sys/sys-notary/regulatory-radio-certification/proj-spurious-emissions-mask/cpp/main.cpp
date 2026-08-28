#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <expected>
#include <algorithm>
#include <limits>

enum class SpectrumTestError {
    EmptyScanData,
    FailBandEdgeLow,
    FailBandEdgeHigh,
    FailRestrictedBand,
    FailEtsiSpuriousSub1G,
    FailEtsiSpuriousAbove1G
};

struct SpectrumPoint {
    double freq_hz;
    double power_dbm;
};

struct SpectrumValidationReport {
    double fundamental_freq_hz{0.0};
    double fundamental_peak_dbm{-std::numeric_limits<double>::infinity()};
    double worst_band_edge_margin_db{std::numeric_limits<double>::infinity()};
    double worst_spurious_freq_hz{0.0};
    double worst_spurious_power_dbm{-std::numeric_limits<double>::infinity()};
};

class SpectrumMaskValidator {
public:
    constexpr SpectrumMaskValidator(double band_start, double band_end) noexcept
        : band_start_hz_(band_start), band_end_hz_(band_end) {}

    [[nodiscard]] std::expected<SpectrumValidationReport, SpectrumTestError>
    validate(std::span<const SpectrumPoint> scan_data) const noexcept {
        if (scan_data.empty()) {
            return std::unexpected(SpectrumTestError::EmptyScanData);
        }

        SpectrumValidationReport report;

        // Пошук піку основного сигналу в дозволеній смузі
        for (const auto& pt : scan_data) {
            if (pt.freq_hz >= band_start_hz_ && pt.freq_hz <= band_end_hz_) {
                if (pt.power_dbm > report.fundamental_peak_dbm) {
                    report.fundamental_peak_dbm = pt.power_dbm;
                    report.fundamental_freq_hz = pt.freq_hz;
                }
            }
        }

        const double band_edge_limit_dbm = report.fundamental_peak_dbm - 20.0;

        for (const auto& pt : scan_data) {
            const double f = pt.freq_hz;
            const double p = pt.power_dbm;

            if (f >= band_start_hz_ && f <= band_end_hz_) {
                continue;
            }

            // Перевірка смуг обмеженого використання (FCC Restricted Bands)
            if (is_fcc_restricted_band(f)) {
                constexpr double kFccRestrictedLimitDbm = -41.2;
                if (p > kFccRestrictedLimitDbm) {
                    report.worst_spurious_freq_hz = f;
                    report.worst_spurious_power_dbm = p;
                    return std::unexpected(SpectrumTestError::FailRestrictedBand);
                }
            }

            // Перевірка спадання на краях смуги (Band Edges)
            if ((f >= band_start_hz_ - 20.0e6 && f < band_start_hz_) ||
                (f > band_end_hz_ && f <= band_end_hz_ + 20.0e6)) {
                const double margin = band_edge_limit_dbm - p;
                report.worst_band_edge_margin_db = std::min(report.worst_band_edge_margin_db, margin);

                if (p > band_edge_limit_dbm) {
                    report.worst_spurious_freq_hz = f;
                    report.worst_spurious_power_dbm = p;
                    return std::unexpected(f < band_start_hz_ ?
                        SpectrumTestError::FailBandEdgeLow : SpectrumTestError::FailBandEdgeHigh);
                }
            }

            // Перевірка позасмугових побічних випромінювань (ETSI)
            if (f < 1.0e9) {
                if (p > -36.0) {
                    report.worst_spurious_freq_hz = f;
                    report.worst_spurious_power_dbm = p;
                    return std::unexpected(SpectrumTestError::FailEtsiSpuriousSub1G);
                }
            } else {
                if (p > -30.0) {
                    report.worst_spurious_freq_hz = f;
                    report.worst_spurious_power_dbm = p;
                    return std::unexpected(SpectrumTestError::FailEtsiSpuriousAbove1G);
                }
            }

            if (p > report.worst_spurious_power_dbm) {
                report.worst_spurious_power_dbm = p;
                report.worst_spurious_freq_hz = f;
            }
        }

        return report;
    }

private:
    [[nodiscard]] static constexpr bool is_fcc_restricted_band(double f_hz) noexcept {
        return (f_hz >= 2310.0e6 && f_hz <= 2390.0e6) ||
               (f_hz >= 2483.5e6 && f_hz <= 2500.0e6) ||
               (f_hz >= 4800.0e6 && f_hz <= 4960.0e6) ||
               (f_hz >= 7200.0e6 && f_hz <= 7440.0e6);
    }

    double band_start_hz_;
    double band_end_hz_;
};
