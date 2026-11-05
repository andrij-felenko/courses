#include "service_calculator.hpp"
#include <iostream>
#include <iomanip>

void ServiceCalculator::addNode(std::unique_ptr<FrictionNode> node) {
    if (node) {
        nodes_.push_back(std::move(node));
    }
}

void ServiceCalculator::logMotion(std::string_view node_name, double distance_mm, double speed_mm_s) {
    for (auto& node : nodes_) {
        if (node->getName() == node_name) {
            node->recordMovement(distance_mm, speed_mm_s);
            return;
        }
    }
}

double ServiceCalculator::getTotalGreaseRequiredMl() const noexcept {
    double total_ml = 0.0;
    for (const auto& node : nodes_) {
        if (node->isMaintenanceRequired()) {
            total_ml += node->calculateRequiredGreaseVolumeMl();
        }
    }
    return total_ml;
}

std::vector<std::string> ServiceCalculator::getNodesRequiringService() const {
    std::vector<std::string> alert_list;
    for (const auto& node : nodes_) {
        if (node->isMaintenanceRequired()) {
            alert_list.emplace_back(node->getName());
        }
    }
    return alert_list;
}

bool ServiceCalculator::serviceNode(std::string_view node_name) {
    for (auto& node : nodes_) {
        if (node->getName() == node_name) {
            node->performService();
            return true;
        }
    }
    return false;
}

void ServiceCalculator::printStatusReport() const {
    std::cout << "\n====================================================================\n";
    std::cout << "        ЗВІТ СЕРВІСНОГО КАЛЬКУЛЯТОРА КІНЕМАТИКИ 3D-ПРИНТЕРА         \n";
    std::cout << "====================================================================\n";
    std::cout << std::left << std::setw(18) << "Вузол"
              << std::setw(14) << "Пробіг (м)"
              << std::setw(14) << "Плівка (мкм)"
              << std::setw(14) << "Ресурс (%)"
              << "Статус ТО\n";
    std::cout << "--------------------------------------------------------------------\n";

    for (const auto& node : nodes_) {
        bool needs_maint = node->isMaintenanceRequired();
        std::cout << std::left << std::setw(18) << node->getName()
                  << std::fixed << std::setprecision(2)
                  << std::setw(14) << node->getTotalTravelMeters()
                  << std::setw(14) << node->getCurrentFilmThicknessUm()
                  << std::setw(14) << node->getGreaseRemainingPercent()
                  << (needs_maint ? "[УВАГА: ПОТРІБНЕ ТО]" : "[НОРМА]") << "\n";
    }

    std::cout << "--------------------------------------------------------------------\n";
    double needed_ml = getTotalGreaseRequiredMl();
    std::cout << "Сумарна потреба в силіконовій змазці SI-180: " 
              << std::fixed << std::setprecision(2) << needed_ml << " мл\n";
    std::cout << "====================================================================\n";
}
