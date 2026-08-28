#include <iostream>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>

enum class Impedance {
    Ohm50 = 50,
    Ohm75 = 75,
    Ohm600 = 600
};

enum class ConversionError {
    InvalidInput,
    NonPositivePower
};

class RfUnitConverter {
public:
    static constexpr double ThermalNoiseFloorDbmHz = -173.98;
    static constexpr double DipoleOffsetDbi = 2.15;

    [[nodiscard]] static constexpr double dbmToMw(double dbm) noexcept {
        return std::pow(10.0, dbm / 10.0);
    }

    [[nodiscard]] static std::expected<double, ConversionError> mwToDbm(double mw) noexcept {
        if (mw <= 0.0) {
            return std::unexpected(ConversionError::NonPositivePower);
        }
        return 10.0 * std::log10(mw);
    }

    [[nodiscard]] static constexpr double dbmToDbw(double dbm) noexcept {
        return dbm - 30.0;
    }

    [[nodiscard]] static constexpr double dbwToDbm(double dbw) noexcept {
        return dbw + 30.0;
    }

    [[nodiscard]] static constexpr double dbmuvToDbm(double dbmuv, Impedance z) noexcept {
        double k = (z == Impedance::Ohm75) ? 108.75 : 106.99;
        return dbmuv - k;
    }

    [[nodiscard]] static constexpr double dbmToDbmuv(double dbm, Impedance z) noexcept {
        double k = (z == Impedance::Ohm75) ? 108.75 : 106.99;
        return dbm + k;
    }

    [[nodiscard]] static constexpr double dbdToDbi(double dbd) noexcept {
        return dbd + DipoleOffsetDbi;
    }

    [[nodiscard]] static constexpr double dbiToDbd(double dbi) noexcept {
        return dbi - DipoleOffsetDbi;
    }

    [[nodiscard]] static std::expected<double, ConversionError> calculateCn0(double signalDbm, double bandwidthHz) noexcept {
        if (bandwidthHz <= 0.0) {
            return std::unexpected(ConversionError::InvalidInput);
        }
        return signalDbm - ThermalNoiseFloorDbmHz;
    }
};

int main() {
    constexpr double pDbm = 20.0;
    constexpr double gainDbd = 9.0;

    std::cout << "=== RF Unit Converter (C++23) ===\n";
    std::cout << "Потужність: " << pDbm << " dBm = " << RfUnitConverter::dbmToMw(pDbm) 
              << " мВт = " << RfUnitConverter::dbmToDbw(pDbm) << " dBW\n";

    std::cout << "Напруга у 50 Ом: " << pDbm << " dBm = " 
              << RfUnitConverter::dbmToDbmuv(pDbm, Impedance::Ohm50) << " dBuV\n";

    std::cout << "Підсилення антени: " << gainDbd << " dBd = " 
              << RfUnitConverter::dbdToDbi(gainDbd) << " dBi\n";

    if (auto cn0 = RfUnitConverter::calculateCn0(-90.0, 20e6); cn0.has_value()) {
        std::cout << "C/N0 при -90 dBm у смузі 20 МГц: " << cn0.value() << " dBHz\n";
    }

    return 0;
}
