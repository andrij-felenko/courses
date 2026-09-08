#include "link_budget.hpp"
#include <cmath>
#include <sstream>
#include <iomanip>

namespace rf {

LinkBudget::LinkBudget(LinkParameters params) : params_(params) {
    validate();
}

void LinkBudget::validate() const {
    if (params_.freq_mhz <= 0.0) {
        throw std::invalid_argument("Частота повинна бути додатною (> 0 МГц).");
    }
    if (params_.distance_km <= 0.0) {
        throw std::invalid_argument("Дистанція повинна бути додатною (> 0 км).");
    }
    if (params_.tx_power_dbm < -40.0 || params_.tx_power_dbm > 60.0) {
        throw std::invalid_argument("Потужність передавача поза межами [-40..+60 дБм].");
    }
    if (params_.rx_sensitivity_dbm < -160.0 || params_.rx_sensitivity_dbm > 0.0) {
        throw std::invalid_argument("Чутливість приймача поза межами [-160..0 дБм].");
    }
}

void LinkBudget::set_distance(double km) {
    if (km <= 0.0) throw std::invalid_argument("Неприпустима дистанція.");
    params_.distance_km = km;
}

void LinkBudget::set_tx_power(double dbm) {
    if (dbm < -40.0 || dbm > 60.0) throw std::invalid_argument("Неприпустима потужність.");
    params_.tx_power_dbm = dbm;
}

LinkReport LinkBudget::evaluate() const {
    LinkReport report;

    // Втрати у вільному просторі (FSPL) за рівнянням Фріїса
    report.fspl_db = 20.0 * std::log10(params_.distance_km) +
                     20.0 * std::log10(params_.freq_mhz) + 32.44;

    // Еквівалентна випромінювана потужність (EIRP)
    report.eirp_dbm = params_.tx_power_dbm + params_.tx_gain_dbi - params_.tx_loss_db;

    // Рівень сигналу на вході приймача (Prx)
    report.prx_dbm = report.eirp_dbm + params_.rx_gain_dbi - params_.rx_loss_db - report.fspl_db;

    // Запас на завмирання (Fade Margin)
    report.margin_db = report.prx_dbm - params_.rx_sensitivity_dbm;
    report.is_reliable = (report.margin_db >= 10.0);

    return report;
}

std::string LinkReport::format() const {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(2);
    ss << "\n==================================================\n";
    ss << "          РОЗРАХУНОК ЕНЕРГЕТИЧНОГО БЮДЖЕТУ        \n";
    ss << "==================================================\n";
    ss << "Втрати у просторі (FSPL): " << std::setw(8) << fspl_db << " дБ\n";
    ss << "Випромінювана потужність: " << std::setw(8) << eirp_dbm << " дБм\n";
    ss << "Очікуваний сигнал Prx:    " << std::setw(8) << prx_dbm << " дБм\n";
    ss << "Запас каналу (Margin):    " << std::setw(8) << margin_db << " дБ\n";
    ss << "--------------------------------------------------\n";
    if (is_reliable) {
        ss << "ВЕРДИКТ: [ НАДІЙНЕ З'ЄДНАННЯ ] (Margin >= 10 дБ)\n";
    } else if (margin_db > 0.0) {
        ss << "ВЕРДИКТ: [ ГРАНИЧНИЙ ЛІНК ] (високий ризик втрати пакетів)\n";
    } else {
        ss << "ВЕРДИКТ: [ ЗВ'ЯЗОК ВІДСУТНІЙ ] (сигнал нижче рівня чутливості)\n";
    }
    ss << "==================================================\n";
    return ss.str();
}

} // namespace rf
