// cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <string_view>
#include <array>

class QuantumFermiGas {
public:
    // Константи фізики у системі SI
    static constexpr double Hbar = 1.054571817e-34;       // Дж·с
    static constexpr double ElectronMass = 9.1093837015e-31; // кг
    static constexpr double SpeedOfLight = 299792458.0;   // м/с
    static constexpr double BoltzmannK = 1.380649e-23;    // Дж/К
    static constexpr double EvToJoule = 1.602176634e-19;  // Дж/еВ

    struct PhysicalState {
        double electronDensity;  // m⁻³
        double fermiMomentum;    // kg·m/s
        double fermiVelocity;    // m/s
        double fermiEnergyEv;    // eV
        double fermiTemperature; // K
        double totalKineticEnergy;// J
        double degeneracyPressure;// Pa
        bool isRelativistic;     // true/false
    };

    // Обчислення густини станів g(E)
    [[nodiscard]] static constexpr double densityOfStates(double energyJoules, double volumeM3) noexcept {
        if (energyJoules <= 0.0) return 0.0;
        const double factor = (volumeM3 / (2.0 * std::numbers::pi * std::numbers::pi)) *
                              std::pow(2.0 * ElectronMass / (Hbar * Hbar), 1.5);
        return factor * std::sqrt(energyJoules);
    }

    // Розподіл Фермі — Дірака
    [[nodiscard]] static double fermiDiracDistribution(double energyJoules, double chemicalPotentialJ, double tempK) noexcept {
        if (tempK <= 0.0) {
            return (energyJoules <= chemicalPotentialJ) ? 1.0 : 0.0;
        }
        const double arg = (energyJoules - chemicalPotentialJ) / (BoltzmannK * tempK);
        if (arg > 700.0) return 0.0;
        if (arg < -700.0) return 1.0;
        return 1.0 / (std::exp(arg) + 1.0);
    }

    // Обчислення стану виродженого газу
    [[nodiscard]] static PhysicalState simulate(double totalElectrons, double volumeM3) noexcept {
        const double n_e = totalElectrons / volumeM3;
        const double k_F = std::cbrt(3.0 * std::numbers::pi * std::numbers::pi * n_e);
        const double p_F = Hbar * k_F;
        const double v_F = p_F / ElectronMass;

        const double restEnergyJ = ElectronMass * SpeedOfLight * SpeedOfLight;
        const double nonRelEnergyJ = (p_F * p_F) / (2.0 * ElectronMass);

        PhysicalState state{};
        state.electronDensity = n_e;
        state.fermiMomentum = p_F;
        state.fermiVelocity = v_F;

        if (nonRelEnergyJ > 0.1 * restEnergyJ) {
            state.isRelativistic = true;
            const double totalE = std::sqrt(p_F * p_F * SpeedOfLight * SpeedOfLight + restEnergyJ * restEnergyJ);
            const double relEnergyJ = totalE - restEnergyJ;
            state.fermiEnergyEv = relEnergyJ / EvToJoule;
            state.totalKineticEnergy = 0.75 * totalElectrons * relEnergyJ;
            state.degeneracyPressure = 0.25 * n_e * relEnergyJ;
        } else {
            state.isRelativistic = false;
            state.fermiEnergyEv = nonRelEnergyJ / EvToJoule;
            state.totalKineticEnergy = 0.60 * totalElectrons * nonRelEnergyJ;
            state.degeneracyPressure = 0.40 * n_e * nonRelEnergyJ;
        }

        state.fermiTemperature = (state.fermiEnergyEv * EvToJoule) / BoltzmannK;
        return state;
    }
};

void printReport(std::string_view label, const QuantumFermiGas::PhysicalState& st) {
    std::cout << "==================================================\n"
              << " СИСТЕМА: " << label << "\n"
              << "==================================================\n"
              << " Режим:                      " << (st.isRelativistic ? "РЕЛЯТИВІСТСЬКИЙ" : "Нерелятивістський") << "\n"
              << " Концентрація e⁻ (n_e):      " << std::scientific << std::setprecision(3) << st.electronDensity << " m⁻³\n"
              << " Імпульс Фермі (p_F):        " << st.fermiMomentum << " kg·m/s\n"
              << " Швидкість Фермі (v_F):      " << st.fermiVelocity << " m/s (" 
              << std::fixed << std::setprecision(2) << (st.fermiVelocity / QuantumFermiGas::SpeedOfLight) * 100.0 << "% c)\n"
              << " Енергія Фермі (E_F):        " << std::fixed << std::setprecision(3) << st.fermiEnergyEv << " eV\n"
              << " Температура Фермі (T_F):    " << std::fixed << std::setprecision(1) << st.fermiTemperature << " K\n"
              << " Повна енергія (T=0 K):      " << std::scientific << std::setprecision(3) << st.totalKineticEnergy << " J\n"
              << " Тиск виродження (P_deg):    " << st.degeneracyPressure << " Pa (" 
              << (st.degeneracyPressure / 101325.0) << " atm)\n\n";
}

int main() {
    constexpr double sampleVolume = 1.0e-6; // 1 cm³

    // 1. Мідний провідник (Cu)
    const auto cu = QuantumFermiGas::simulate(8.47e28 * sampleVolume, sampleVolume);
    printReport("Мідний провідник (Cu, 1 cm³)", cu);

    // 2. Металевий Натрій (Na)
    const auto na = QuantumFermiGas::simulate(2.65e28 * sampleVolume, sampleVolume);
    printReport("Металевий Натрій (Na, 1 cm³)", na);

    // 3. Зорі — Білі Карлики
    const auto wd = QuantumFermiGas::simulate(1.0e36 * sampleVolume, sampleVolume);
    printReport("Надра Білого Карлика (1 cm³)", wd);

    return 0;
}
