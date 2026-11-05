#include "abbe_compensator.hpp"
#include "compensation_table.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <stdexcept>

AbbeCompensator::AbbeCompensator(const AbbeArm& arm, AngleUnit unit)
    : arm_(arm), unit_(unit) {}

AbbeCompensator::AbbeCompensator(double dy_mm, double dz_mm, AngleUnit unit)
    : arm_{dy_mm, dz_mm}, unit_(unit) {}

void AbbeCompensator::setArm(const AbbeArm& arm) noexcept {
    arm_ = arm;
}

void AbbeCompensator::setArm(double dy_mm, double dz_mm) noexcept {
    arm_ = AbbeArm{dy_mm, dz_mm};
}

const AbbeArm& AbbeCompensator::arm() const noexcept {
    return arm_;
}

void AbbeCompensator::setAngleUnit(AngleUnit unit) noexcept {
    unit_ = unit;
}

AngleUnit AbbeCompensator::angleUnit() const noexcept {
    return unit_;
}

bool AbbeCompensator::addSample(const InterferometerSample& sample) {
    if (!std::isfinite(sample.position_x) ||
        !std::isfinite(sample.pitch) ||
        !std::isfinite(sample.yaw)) {
        return false;
    }
    samples_.push_back(sample);
    return true;
}

bool AbbeCompensator::addSample(double position_x, double pitch, double yaw) {
    return addSample(InterferometerSample{position_x, pitch, yaw});
}

std::size_t AbbeCompensator::addSamples(const std::vector<InterferometerSample>& samples) {
    std::size_t addedCount = 0;
    samples_.reserve(samples_.size() + samples.size());
    for (const auto& sample : samples) {
        if (addSample(sample)) {
            ++addedCount;
        }
    }
    return addedCount;
}

void AbbeCompensator::clearSamples() noexcept {
    samples_.clear();
}

const std::vector<InterferometerSample>& AbbeCompensator::samples() const noexcept {
    return samples_;
}

std::size_t AbbeCompensator::sampleCount() const noexcept {
    return samples_.size();
}

double AbbeCompensator::toRadians(double angle, AngleUnit unit) noexcept {
    switch (unit) {
        case AngleUnit::Arcseconds:
            return angle * ARCSEC_TO_RAD;
        case AngleUnit::Microradians:
            return angle * URAD_TO_RAD;
        case AngleUnit::Milliradians:
            return angle * MRAD_TO_RAD;
        case AngleUnit::Radians:
        default:
            return angle;
    }
}

std::optional<AngleUnit> AbbeCompensator::parseAngleUnit(std::string_view str) noexcept {
    // Пропуск пробілів на початку і в кінці
    while (!str.empty() && std::isspace(static_cast<unsigned char>(str.front()))) {
        str.remove_prefix(1);
    }
    while (!str.empty() && std::isspace(static_cast<unsigned char>(str.back()))) {
        str.remove_suffix(1);
    }

    if (str.empty()) {
        return std::nullopt;
    }

    // Приведення до нижнього регістру у локальному буфері
    char buf[32];
    if (str.size() >= sizeof(buf)) {
        return std::nullopt;
    }
    for (std::size_t i = 0; i < str.size(); ++i) {
        buf[i] = static_cast<char>(std::tolower(static_cast<unsigned char>(str[i])));
    }
    const std::string_view lower(buf, str.size());

    if (lower == "arcsec" || lower == "sec" || lower == "as" || lower == "\"") {
        return AngleUnit::Arcseconds;
    }
    if (lower == "urad" || lower == "microrad" || lower == "ur" || lower == "µrad") {
        return AngleUnit::Microradians;
    }
    if (lower == "mrad" || lower == "millirad") {
        return AngleUnit::Milliradians;
    }
    if (lower == "rad" || lower == "radian" || lower == "radians") {
        return AngleUnit::Radians;
    }

    return std::nullopt;
}

std::string_view AbbeCompensator::angleUnitToString(AngleUnit unit) noexcept {
    switch (unit) {
        case AngleUnit::Arcseconds:
            return "arcsec";
        case AngleUnit::Microradians:
            return "urad";
        case AngleUnit::Milliradians:
            return "mrad";
        case AngleUnit::Radians:
            return "rad";
        default:
            return "unknown";
    }
}

CompensationEntry AbbeCompensator::calculatePoint(const InterferometerSample& sample) const noexcept {
    const double pitch_rad = toRadians(sample.pitch, unit_);
    const double yaw_rad   = toRadians(sample.yaw, unit_);

    /*
     * Кінематична модель лінійної похибки Аббе першого порядку для малих кутів (sin(θ) ≈ θ):
     * 1. Кутове відхилення тангажу (pitch, навколо осі Y) створює паразитне зміщення вздовж X
     *    через вертикальне плече dz:
     *      error_pitch = dz * pitch_rad
     * 2. Кутове відхилення рискання (yaw, навколо осі Z) створює паразитне зміщення вздовж X
     *    через горизонтальне плече dy:
     *      error_yaw = dy * yaw_rad
     * 3. Сумарна поздовжня похибка позиціонування:
     *      total_error = error_pitch + error_yaw
     * 4. Компенсуюча поправка системи керування протилежна за знаком:
     *      correction = -total_error
     * Скоригована координата: X_corr = X_nom + correction = X_nom - total_error
     */
    const double error_pitch = arm_.dz * pitch_rad;
    const double error_yaw   = arm_.dy * yaw_rad;
    const double total_error = error_pitch + error_yaw;

    return CompensationEntry{
        sample.position_x,
        pitch_rad,
        yaw_rad,
        error_pitch,
        error_yaw,
        total_error,
        -total_error
    };
}

CompensationEntry AbbeCompensator::calculatePoint(double position_x, double pitch, double yaw) const noexcept {
    return calculatePoint(InterferometerSample{position_x, pitch, yaw});
}

CompensationTable AbbeCompensator::generateTable() const {
    if (samples_.size() < 2) {
        throw std::runtime_error(
            "Неможливо сформувати таблицю компенсації: потрібно щонайменше 2 виміри інтерферометра.");
    }

    // Створюємо копію замірів і впорядковуємо за зростанням координати X
    std::vector<InterferometerSample> sortedSamples = samples_;
    std::sort(sortedSamples.begin(), sortedSamples.end(),
        [](const InterferometerSample& a, const InterferometerSample& b) {
            return a.position_x < b.position_x;
        });

    std::vector<CompensationEntry> entries;
    entries.reserve(sortedSamples.size());

    for (const auto& sample : sortedSamples) {
        entries.push_back(calculatePoint(sample));
    }

    return CompensationTable(std::move(entries), arm_);
}
