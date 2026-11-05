#include "EnclosureJointCalculator.hpp"
#include <cmath>
#include <iostream>
#include <algorithm>

VerificationReport EnclosureJointCalculator::calculate(double plate_thickness, MaterialType mat, FastenerGrade grade) const {
    VerificationReport report;
    report.plate_thickness = plate_thickness;
    report.mat_type = mat;
    report.grade = grade;

    // Геометричні параметри потайного гвинта М3 DIN 7991:
    // Номінальний діаметр d = 3.0 мм
    // Зовнішній діаметр головки dk ≈ 6.0 мм
    // Кут зенкування alpha = 90° (половина кута beta = 45°)
    const double d = 3.0;
    const double dk = 6.0;
    const double alpha_deg = 90.0;
    const double beta_rad = (alpha_deg / 2.0) * (M_PI / 180.0);

    // Глибина конуса зенкування h_k
    const double d_pilot = 2.5;
    report.h_k = (dk / 2.0 - d_pilot / 2.0) / std::tan(beta_rad);

    // Залишкова товщина циліндричної частини (пояска) t_cyl
    report.t_cyl = plate_thickness - report.h_k;

    // Перевірка на дефект knife-edge (гострий ніж)
    const double min_safe_t_cyl = 0.5;
    report.knife_edge_warning = (report.t_cyl < min_safe_t_cyl);

    // Контактна площа конуса (усічений конус)
    double r_max = dk / 2.0;
    double r_min = d_pilot / 2.0;
    double slant_height = std::sqrt(report.h_k * report.h_k + (r_max - r_min) * (r_max - r_min));
    report.contact_area = M_PI * (r_max + r_min) * slant_height;

    // Визначення допустимого моменту затягування T_tight та попередження для шестигранника 2.0 мм
    switch (grade) {
        case FastenerGrade::A2_70:
            report.T_tight = 0.8; // Н·м
            report.hex_strip_warning = "Увага: A2-70 має м'яку неіржавну сталь, шестигранник 2.0 мм може злизатися при перевищенні 0.8 Н·м.";
            break;
        case FastenerGrade::Grade10_9:
            report.T_tight = 1.2; // Н·м
            report.hex_strip_warning = "Увага: Клас 10.9 міцніший, але шліц 2.0 мм вимагає якісного шестигранного ключа та зусилля до 1.2 Н·м.";
            break;
        case FastenerGrade::Grade12_9:
            report.T_tight = 1.4; // Н·м
            report.hex_strip_warning = "Критично: Клас 12.9 створює високе навантаження на шліц 2.0 мм, ризик зриву граней високий!";
            break;
    }

    // Попереднє натягнення гвинта F_pre
    const double K_torque_coeff = 0.2;
    double F_pre = (report.T_tight) / (K_torque_coeff * (d / 1000.0));

    // Контактний тиск P_contact = F_pre / A_contact (в МПа або Н/мм²)
    report.contact_pressure = (report.contact_area > 0.0) ? (F_pre / report.contact_area) : 0.0;

    // Границя міцності матеріалу на стиск (орієнтовно)
    double allowable_pressure = 100.0;
    switch (mat) {
        case MaterialType::Aluminum6061:
            allowable_pressure = 150.0;
            break;
        case MaterialType::Steel:
            allowable_pressure = 300.0;
            break;
        case MaterialType::Thermoplastic:
            allowable_pressure = 45.0;
            break;
        case MaterialType::Fr4:
            allowable_pressure = 200.0;
            break;
    }

    report.is_passed = (!report.knife_edge_warning) && (report.contact_pressure <= allowable_pressure);

    return report;
}

void EnclosureJointCalculator::printReport(const VerificationReport& report) const {
    std::cout << "=== Звіт верифікації конічного з'єднання М3 (DIN 7991) ===\n";
    std::cout << "Товщина пластини: " << report.plate_thickness << " мм\n";
    std::cout << "Глибина конуса (h_k): " << report.h_k << " мм\n";
    std::cout << "Залишкова товщина (t_cyl): " << report.t_cyl << " мм\n";
    std::cout << "Контактна площа: " << report.contact_area << " мм²\n";
    std::cout << "Момент затягування (T_tight): " << report.T_tight << " Н·м\n";
    std::cout << "Контактний тиск: " << report.contact_pressure << " МПа\n";
    
    if (report.knife_edge_warning) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] Виявлено ризик дефекту 'knife-edge' (занадто тонкий залишковий поясок)!\n";
    } else {
        std::cout << "[ОК] Товщина стінки безпечна від knife-edge.\n";
    }

    std::cout << report.hex_strip_warning << "\n";

    if (report.is_passed) {
        std::cout << "Статус верифікації: УСПІШНО (З'єднання надійне)\n";
    } else {
        std::cout << "Статус верифікації: НЕ ПРОЙДЕНО (Перевищено допустимі навантаження або критична геометрія)\n";
    }
}
