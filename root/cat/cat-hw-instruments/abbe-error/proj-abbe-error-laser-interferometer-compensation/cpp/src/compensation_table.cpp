#include "compensation_table.hpp"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>

CompensationTable::CompensationTable(std::vector<CompensationEntry> entries, const AbbeArm& arm)
    : entries_(std::move(entries)), arm_(arm) {}

const std::vector<CompensationEntry>& CompensationTable::entries() const noexcept {
    return entries_;
}

std::size_t CompensationTable::size() const noexcept {
    return entries_.size();
}

bool CompensationTable::empty() const noexcept {
    return entries_.empty();
}

const AbbeArm& CompensationTable::arm() const noexcept {
    return arm_;
}

CompensationTable::ValidationResult CompensationTable::validate(double stepTolerance) const {
    ValidationResult res;
    if (entries_.size() < 2) {
        res.isValid = false;
        res.isMonotonic = false;
        res.isUniformStep = false;
        res.nominalStepMm = 0.0;
        res.message = "Помилка калібрувальної сітки: таблиця містить менше 2 опорних точок.";
        return res;
    }

    res.isMonotonic = true;
    res.isUniformStep = true;
    const double nominalStep = entries_[1].position_x - entries_[0].position_x;

    if (nominalStep <= 0.0) {
        res.isMonotonic = false;
        res.isUniformStep = false;
        res.nominalStepMm = nominalStep;
        res.isValid = false;
        res.message = "Помилка калібрувальної сітки: перші дві точки не утворюють строго додатного інтервалу.";
        return res;
    }

    res.nominalStepMm = nominalStep;

    for (std::size_t i = 1; i < entries_.size(); ++i) {
        const double delta = entries_[i].position_x - entries_[i - 1].position_x;
        if (delta <= 0.0) {
            res.isMonotonic = false;
            res.isUniformStep = false;
            res.isValid = false;
            res.message = "Помилка калібрувальної сітки: порушено строгу монотонність у точці X="
                        + std::to_string(entries_[i].position_x) + " мм.";
            return res;
        }

        if (std::abs(delta - nominalStep) > stepTolerance) {
            res.isUniformStep = false;
        }
    }

    res.isValid = res.isMonotonic;
    if (!res.isUniformStep) {
        res.message = "Калібрувальна сітка монотонна, але крок нерівномірний (потрібна кусочно-лінійна інтерполяція).";
    } else {
        res.message = "Калібрувальна сітка коректна: строго монотонна та має стабільний крок "
                    + std::to_string(nominalStep) + " мм.";
    }

    return res;
}

bool CompensationTable::isMonotonic() const noexcept {
    if (entries_.size() < 2) {
        return false;
    }
    for (std::size_t i = 1; i < entries_.size(); ++i) {
        if (entries_[i].position_x <= entries_[i - 1].position_x) {
            return false;
        }
    }
    return true;
}

bool CompensationTable::isUniformStep(double stepTolerance, double* stepOut) const noexcept {
    if (entries_.size() < 2) {
        return false;
    }
    const double nominalStep = entries_[1].position_x - entries_[0].position_x;
    if (nominalStep <= 0.0) {
        return false;
    }
    for (std::size_t i = 1; i < entries_.size(); ++i) {
        const double delta = entries_[i].position_x - entries_[i - 1].position_x;
        if (std::abs(delta - nominalStep) > stepTolerance) {
            return false;
        }
    }
    if (stepOut != nullptr) {
        *stepOut = nominalStep;
    }
    return true;
}

double CompensationTable::interpolateCorrection(double position_x) const {
    if (entries_.empty()) {
        return 0.0;
    }
    if (entries_.size() == 1) {
        return entries_.front().correction_mm;
    }

    // Обмеження значення на границях виміряного діапазону (clamping)
    if (position_x <= entries_.front().position_x) {
        return entries_.front().correction_mm;
    }
    if (position_x >= entries_.back().position_x) {
        return entries_.back().correction_mm;
    }

    // Швидкий логарифмічний пошук O(log N) інтервалу [prev, it]
    auto it = std::lower_bound(entries_.begin(), entries_.end(), position_x,
        [](const CompensationEntry& entry, double val) {
            return entry.position_x < val;
        });

    if (it == entries_.begin()) {
        return it->correction_mm;
    }

    const auto prev = it - 1;
    const double span = it->position_x - prev->position_x;
    if (span <= 0.0) {
        return prev->correction_mm;
    }

    const double t = (position_x - prev->position_x) / span;
    return prev->correction_mm + t * (it->correction_mm - prev->correction_mm);
}

double CompensationTable::interpolateError(double position_x) const {
    if (entries_.empty()) {
        return 0.0;
    }
    if (entries_.size() == 1) {
        return entries_.front().total_error_mm;
    }

    if (position_x <= entries_.front().position_x) {
        return entries_.front().total_error_mm;
    }
    if (position_x >= entries_.back().position_x) {
        return entries_.back().total_error_mm;
    }

    auto it = std::lower_bound(entries_.begin(), entries_.end(), position_x,
        [](const CompensationEntry& entry, double val) {
            return entry.position_x < val;
        });

    if (it == entries_.begin()) {
        return it->total_error_mm;
    }

    const auto prev = it - 1;
    const double span = it->position_x - prev->position_x;
    if (span <= 0.0) {
        return prev->total_error_mm;
    }

    const double t = (position_x - prev->position_x) / span;
    return prev->total_error_mm + t * (it->total_error_mm - prev->total_error_mm);
}

CompensationTable::Statistics CompensationTable::statistics() const noexcept {
    Statistics stats{};
    if (entries_.empty()) {
        return stats;
    }

    stats.pointCount = entries_.size();
    stats.startPosMm = entries_.front().position_x;
    stats.endPosMm   = entries_.back().position_x;
    stats.minErrorMm = entries_.front().total_error_mm;
    stats.maxErrorMm = entries_.front().total_error_mm;
    stats.maxCorrectionMm = std::abs(entries_.front().correction_mm);

    for (const auto& entry : entries_) {
        stats.minErrorMm = std::min(stats.minErrorMm, entry.total_error_mm);
        stats.maxErrorMm = std::max(stats.maxErrorMm, entry.total_error_mm);
        stats.maxCorrectionMm = std::max(stats.maxCorrectionMm, std::abs(entry.correction_mm));
    }

    stats.peakToPeakMm = stats.maxErrorMm - stats.minErrorMm;
    return stats;
}

void CompensationTable::exportCsv(std::ostream& os) const {
    os << "Position_mm,Pitch_rad,Yaw_rad,Error_Pitch_um,Error_Yaw_um,Total_Error_um,Correction_um\n";
    os << std::fixed;
    for (const auto& e : entries_) {
        os << std::setprecision(4) << e.position_x << ","
           << std::setprecision(9) << e.pitch_rad << ","
           << std::setprecision(9) << e.yaw_rad << ","
           << std::setprecision(4) << (e.error_pitch_mm * 1000.0) << ","
           << std::setprecision(4) << (e.error_yaw_mm * 1000.0) << ","
           << std::setprecision(4) << (e.total_error_mm * 1000.0) << ","
           << std::setprecision(4) << (e.correction_mm * 1000.0) << "\n";
    }
}

void CompensationTable::exportFanuc(std::ostream& os, int startParam, std::string_view axisName) const {
    os << "%\n";
    os << "(FANUC PITCH ERROR / ABBE COMPENSATION TABLE)\n";
    os << "(AXIS: " << axisName << ", ARM: DY=" << std::fixed << std::setprecision(3)
       << arm_.dy << " MM, DZ=" << arm_.dz << " MM)\n";
    os << "(TOTAL POINTS: " << entries_.size() << ")\n";

    int param = startParam;
    for (const auto& e : entries_) {
        // У ЧПУ Fanuc значення поправки вказується в дискретах системи (зазвичай 1 мкм або 0.1 мкм)
        const double corr_um = e.correction_mm * 1000.0;
        os << "N" << param++ << " P" << std::setprecision(1) << corr_um
           << " (POS=" << std::setprecision(3) << e.position_x
           << " MM, CORR=" << std::setprecision(4) << corr_um << " UM)\n";
    }
    os << "%\n";
}

void CompensationTable::exportSiemens(std::ostream& os, int tableIndex, std::string_view axisName) const {
    os << "; ======================================================================\n";
    os << "; SIEMENS SINUMERIK 840D / ONE - PITCH / ABBE ERROR COMPENSATION TABLE\n";
    os << "; AXIS: " << axisName << ", ARM: DY=" << std::fixed << std::setprecision(3)
       << arm_.dy << " MM, DZ=" << arm_.dz << " MM\n";
    os << "; ======================================================================\n";

    if (entries_.empty()) {
        os << "M17\n";
        return;
    }

    const double minPos = entries_.front().position_x;
    const double maxPos = entries_.back().position_x;
    const double step = (entries_.size() > 1) ? (entries_[1].position_x - entries_[0].position_x) : 0.0;

    os << "$AN_CEC_INPUT_AXIS[" << tableIndex << "] = (" << axisName << ")\n";
    os << "$AN_CEC_OUTPUT_AXIS[" << tableIndex << "] = (" << axisName << ")\n";
    os << "$AN_CEC_MIN[" << tableIndex << "] = " << std::setprecision(4) << minPos << "\n";
    os << "$AN_CEC_MAX[" << tableIndex << "] = " << std::setprecision(4) << maxPos << "\n";
    os << "$AN_CEC_STEP[" << tableIndex << "] = " << std::setprecision(4) << step << "\n";
    os << "$AN_CEC_DIRECTION[" << tableIndex << "] = 0 ; 0 = двонапрямлена інтерполяція\n";

    for (std::size_t i = 0; i < entries_.size(); ++i) {
        const auto& e = entries_[i];
        os << "$AN_CEC[" << tableIndex << "," << i << "] = "
           << std::setprecision(6) << e.correction_mm
           << " ; POS=" << std::setprecision(3) << e.position_x << " MM, ERR="
           << std::setprecision(4) << (e.total_error_mm * 1000.0) << " UM\n";
    }
    os << "M17\n";
}

void CompensationTable::exportFormat(std::ostream& os, CncFormat format) const {
    switch (format) {
        case CncFormat::Csv:
            exportCsv(os);
            break;
        case CncFormat::Fanuc:
            exportFanuc(os);
            break;
        case CncFormat::Siemens:
            exportSiemens(os);
            break;
    }
}

bool CompensationTable::saveToFile(std::string_view filePath, CncFormat format) const {
    std::ofstream ofs(std::string(filePath));
    if (!ofs.is_open()) {
        return false;
    }
    exportFormat(ofs, format);
    return ofs.good();
}

std::ostream& operator<<(std::ostream& os, const CompensationTable& table) {
    os << "====================================================================================================\n";
    os << "  ТАБЛИЦЯ ЦИФРОВОЇ КОМПЕНСАЦІЇ ПОХИБКИ АББЕ (Плече: dy="
       << std::fixed << std::setprecision(2) << table.arm_.dy << " мм, dz="
       << table.arm_.dz << " мм)\n";
    os << "====================================================================================================\n";
    os << std::right
       << std::setw(10) << "X [мм]" << " | "
       << std::setw(12) << "Pitch [рад]" << " | "
       << std::setw(12) << "Yaw [рад]" << " | "
       << std::setw(13) << "Err Pitch[мкм]" << " | "
       << std::setw(13) << "Err Yaw[мкм]" << " | "
       << std::setw(14) << "Total Err[мкм]" << " | "
       << std::setw(12) << "Corr [мкм]" << "\n";
    os << "----------------------------------------------------------------------------------------------------\n";

    for (const auto& e : table.entries_) {
        os << std::right
           << std::setw(10) << std::setprecision(2) << e.position_x << " | "
           << std::setw(12) << std::setprecision(7) << e.pitch_rad << " | "
           << std::setw(12) << std::setprecision(7) << e.yaw_rad << " | "
           << std::setw(13) << std::setprecision(3) << (e.error_pitch_mm * 1000.0) << " | "
           << std::setw(13) << std::setprecision(3) << (e.error_yaw_mm * 1000.0) << " | "
           << std::setw(14) << std::setprecision(3) << (e.total_error_mm * 1000.0) << " | "
           << std::setw(12) << std::setprecision(3) << (e.correction_mm * 1000.0) << "\n";
    }
    os << "====================================================================================================\n";
    return os;
}
