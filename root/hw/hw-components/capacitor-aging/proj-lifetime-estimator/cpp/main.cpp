#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <span>

enum class CapType {
    MlccClass2,
    AluElectrolytic,
    AluPolymer,
    FilmPP
};

struct ProfileBin {
    double tAmbientC;      // Температура повітря, °C
    double hoursPerYear;   // Напрацювання за рік, годин
    double iRippleRmsA;   // Струм пульсацій через конденсатор, А
    double vAppliedV;     // Робоча напруга, В
};

struct CapacitorSpec {
    std::string_view name;
    CapType type;
    double cNomUf;        // Номінальна ємність, мкФ
    double vRatedV;       // Номінальна напруга, В
    double esrMohm;        // Початковий опір ESR, мОм
    double rThCPerW;      // Тепловий опір корпус-довкілля, °C/Вт
    double lBaseHours;    // Паспортний ресурс при T_max, годин
    double tMaxC;         // Гранична температура, °C
    double agingRatePct;  // Швидкість старіння MLCC (%/декаду)
};

struct AnalysisResult {
    double annualDamage{0.0};       // Накопичене пошкодження за 1 рік (0.0 .. 1.0)
    double expectedLifeYears{0.0};  // Очікуваний термін служби до EoL, років
    double maxTCoreC{-273.15};      // Максимальна температура серцевини, °C
    double finalCUf{0.0};          // Розрахункова ємність на кінець терміну, мкФ
    double finalEsrMohm{0.0};       // Прогнозований ESR на момент EoL, мОм
    bool isReliable{false};         // Прапор придатності для місії > 10 років
};

// Розрахунок ресурсу електролітичного конденсатора за Арреніусом (правило 10 °C)
[[nodiscard]] constexpr double calculateElecLifetimeHours(const CapacitorSpec& spec, double tCoreC, [[maybe_unused]] double vOpV) noexcept {
    const double deltaT = spec.tMaxC - tCoreC;
    const double afTemp = std::pow(2.0, deltaT / 10.0);
    const double afVoltage = 1.0;
    
    return spec.lBaseHours * afTemp * afVoltage;
}

// Розрахунок логарифмічного старіння кераміки MLCC
[[nodiscard]] inline double calculateMlccCapacitance(const CapacitorSpec& spec, double totalOperatingHours) noexcept {
    if (totalOperatingHours <= 1.0) {
        return spec.cNomUf * (1.0 + (spec.agingRatePct / 100.0) * 3.0);
    }
    
    const double decadesFrom1000h = std::log10(totalOperatingHours / 1000.0);
    const double cFactor = 1.0 - (spec.agingRatePct / 100.0) * decadesFrom1000h;
    
    return spec.cNomUf * cFactor;
}

// Аналіз надійності за профілем навантаження (Palmgren-Miner)
[[nodiscard]] AnalysisResult evaluateCapacitorMission(const CapacitorSpec& spec, std::span<const ProfileBin> profile) {
    AnalysisResult res;
    res.finalCUf = spec.cNomUf;
    res.finalEsrMohm = spec.esrMohm;

    double totalAnnualHours = 0.0;

    for (const auto& bin : profile) {
        totalAnnualHours += bin.hoursPerYear;

        // Втрати потужності та нагрів серцевини
        const double pLossW = std::pow(bin.iRippleRmsA, 2.0) * (spec.esrMohm / 1000.0);
        const double deltaTC = pLossW * spec.rThCPerW;
        const double tCoreC = bin.tAmbientC + deltaTC;

        if (tCoreC > res.maxTCoreC) {
            res.maxTCoreC = tCoreC;
        }

        if (spec.type == CapType::AluElectrolytic || spec.type == CapType::AluPolymer) {
            const double lBinHours = calculateElecLifetimeHours(spec, tCoreC, bin.vAppliedV);
            if (lBinHours > 0.0) {
                res.annualDamage += bin.hoursPerYear / lBinHours;
            }
        }
    }

    if (res.annualDamage > 0.0) {
        res.expectedLifeYears = 1.0 / res.annualDamage;
        res.finalEsrMohm = spec.esrMohm * 2.0; // критерій EoL: подвоєння ESR
        res.finalCUf = spec.cNomUf * 0.80;       // спад ємності на 20 %
    } else {
        res.expectedLifeYears = 25.0; // для MLCC та плівки без висихання
    }

    if (spec.type == CapType::MlccClass2) {
        const double hours10y = 10.0 * (totalAnnualHours > 0.0 ? totalAnnualHours : 8760.0);
        res.finalCUf = calculateMlccCapacitance(spec, hours10y);
    }

    res.isReliable = (res.expectedLifeYears >= 10.0) && (res.maxTCoreC <= spec.tMaxC);
    return res;
}

int main() {
    const std::vector<ProfileBin> profile = {
        { .tAmbientC = 35.0, .hoursPerYear = 5000.0, .iRippleRmsA = 1.2, .vAppliedV = 24.0 },
        { .tAmbientC = 55.0, .hoursPerYear = 3000.0, .iRippleRmsA = 1.8, .vAppliedV = 24.0 },
        { .tAmbientC = 75.0, .hoursPerYear =  760.0, .iRippleRmsA = 2.2, .vAppliedV = 24.0 }
    };

    const std::vector<CapacitorSpec> caps = {
        {
            .name = "Alu-Electrolytic Standard (105°C / 2000h)",
            .type = CapType::AluElectrolytic,
            .cNomUf = 470.0, .vRatedV = 35.0, .esrMohm = 65.0,
            .rThCPerW = 42.0, .lBaseHours = 2000.0, .tMaxC = 105.0,
            .agingRatePct = 0.0
        },
        {
            .name = "Alu-Electrolytic Long-Life (105°C / 5000h)",
            .type = CapType::AluElectrolytic,
            .cNomUf = 470.0, .vRatedV = 35.0, .esrMohm = 38.0,
            .rThCPerW = 36.0, .lBaseHours = 5000.0, .tMaxC = 105.0,
            .agingRatePct = 0.0
        },
        {
            .name = "MLCC Array 10x47uF X7R (125°C)",
            .type = CapType::MlccClass2,
            .cNomUf = 470.0, .vRatedV = 50.0, .esrMohm = 3.5,
            .rThCPerW = 12.0, .lBaseHours = 100000.0, .tMaxC = 125.0,
            .agingRatePct = 2.0
        }
    };

    std::cout << "================================================================================\n";
    std::cout << "  АНАЛІЗ РЕСУРСУ ТА СТАРІННЯ КОНДЕНСАТОРІВ (MISSION PROFILE 8760 год/рік)\n";
    std::cout << "================================================================================\n\n";

    std::cout << std::fixed << std::setprecision(1);
    for (const auto& cap : caps) {
        const auto res = evaluateCapacitorMission(cap, profile);

        std::cout << "Конденсатор: " << cap.name << "\n"
                  << "  Максимальна T_core:      " << std::setw(6) << res.maxTCoreC << " °C (ліміт: " << cap.tMaxC << " °C)\n"
                  << "  Річна витрата ресурсу:   " << std::setw(6) << (res.annualDamage * 100.0) << " %\n"
                  << "  Очікуваний ресурс (EoL): " << std::setw(6) << res.expectedLifeYears << " років\n"
                  << "  Ємність через 10 років:  " << std::setw(6) << res.finalCUf << " мкФ (початкова: " << cap.cNomUf << " мкФ)\n"
                  << "  Статус надійності (10р): " << (res.isReliable ? "ПРИДАТНИЙ (PASS)" : "НЕДОСТАТНІЙ РЕСУРС (FAIL)") << "\n\n";
    }

    return 0;
}
