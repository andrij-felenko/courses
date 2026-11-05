#include "bearing_validator.hpp"
#include <algorithm>
#include <sstream>
#include <iomanip>

BearingAssemblyValidator::BearingAssemblyValidator(BearingGeometry geometry)
    : geometry_(std::move(geometry)) {}

double BearingAssemblyValidator::compute_clearance_reduction(double shaft_fit_um, double housing_fit_um) const {
    // Внутрішнє кільце розширюється приблизно на 80% від ефективного натягу вала
    const double inner_expansion = std::max(0.0, shaft_fit_um) * 0.80;
    // Зовнішнє кільце стискається приблизно на 70% від натягу в отворі
    const double outer_contraction = std::max(0.0, housing_fit_um) * 0.70;

    return inner_expansion + outer_contraction;
}

ValidationReport BearingAssemblyValidator::validate(const FitTolerance& fits) const {
    ValidationReport report;

    // Максимальний натяг при найгіршому допуску (найбільший вал, найменший отвір)
    report.shaft_interference_max_um = fits.shaft_dev_max_um;
    report.housing_interference_max_um = -fits.housing_dev_min_um;

    report.clearance_reduction_um = compute_clearance_reduction(
        report.shaft_interference_max_um,
        report.housing_interference_max_um
    );

    report.residual_clearance_um = geometry_.initial_clearance_um - report.clearance_reduction_um;

    // Рекомендований попередній осьовий натяг для вибірки люфту: 0.5% .. 2.0% від C0
    report.preload_recommended_min_n = geometry_.c0_stat_n * 0.005;
    report.preload_recommended_max_n = geometry_.c0_stat_n * 0.020;

    std::ostringstream ss;
    if (report.residual_clearance_um < 1.0) {
        report.is_valid = false;
        ss << "УВАГА: Небезпека заклинювання! Залишковий зазор ("
           << std::fixed << std::setprecision(1) << report.residual_clearance_um
           << " мкм) занадто малий через надмірний натяг.";
    } else {
        report.is_valid = true;
        ss << "Посадка коректна. Залишковий зазор: "
           << std::fixed << std::setprecision(1) << report.residual_clearance_um
           << " мкм. Рекомендоване зусилля натягу: "
           << report.preload_recommended_min_n << ".."
           << report.preload_recommended_max_n << " Н.";
    }

    report.summary_message = ss.str();
    return report;
}
