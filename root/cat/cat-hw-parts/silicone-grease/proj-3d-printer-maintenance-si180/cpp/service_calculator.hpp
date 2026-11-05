#pragma once

#include "friction_node.hpp"
#include <memory>
#include <vector>
#include <string>

/**
 * @brief Менеджер сервісного обслуговування кінематики 3D-принтера.
 * 
 * Агрегує поліморфні вузли тертя, веде журнал пробігу та розраховує потребу в мастилі SI-180.
 */
class ServiceCalculator {
public:
    ServiceCalculator() = default;

    /**
     * @brief Додає кінематичний вузол до списку моніторингу.
     */
    void addNode(std::unique_ptr<FrictionNode> node);

    /**
     * @brief Реєструє переміщення вузла за іменем.
     */
    void logMotion(std::string_view node_name, double distance_mm, double speed_mm_s);

    /**
     * @brief Розраховує сумарний необхідний об'єм змазки SI-180 для вузлів, які потребують ТО.
     */
    [[nodiscard]] double getTotalGreaseRequiredMl() const noexcept;

    /**
     * @brief Повертає список назв вузлів, для яких критично необхідне проведення сервісу.
     */
    [[nodiscard]] std::vector<std::string> getNodesRequiringService() const;

    /**
     * @brief Проводить регламентне скидання стану для зазначеного вузла.
     */
    bool serviceNode(std::string_view node_name);

    /**
     * @brief Виводить у консоль поточний звіт стану кінематики.
     */
    void printStatusReport() const;

private:
    std::vector<std::unique_ptr<FrictionNode>> nodes_;
};
