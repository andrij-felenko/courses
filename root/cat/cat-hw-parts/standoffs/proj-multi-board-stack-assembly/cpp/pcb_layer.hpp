#pragma once

#include <string>
#include <string_view>

/**
 * @brief Перелік типорозмірів метричної різьби стійок.
 */
enum class StandoffThread {
    M2, ///< Різьба M2 x 0.4 мм
    M3  ///< Різьба M3 x 0.5 мм
};

/**
 * @brief Матеріал виготовлення дистанційної стійки.
 */
enum class StandoffMaterial {
    BrassCW614N, ///< Нікельована латунь CW614N (провідний заземлювальний контур)
    NylonPA66    ///< Поліамід PA66 (діелектрик для гальванічної розв'язки)
};

/**
 * @brief Модель одного ярусу друкованої плати в багатоплатному блоці.
 */
struct PcbLayer {
    std::string name;                      ///< Назва або функціональне призначення плати
    double pcb_thickness_mm{1.6};          ///< Товщина текстоліту FR-4 (номінал 1.6 мм)
    double top_components_height_mm{0.0};  ///< Максимальна висота компонентів зверху плати
    double bottom_components_height_mm{0.0};///< Висота SMD деталей знизу плати
    double bottom_leads_protrusion_mm{1.2};///< Довжина вильоту паяних THT виводів знизу плати
    double max_deflection_mm{0.25};        ///< Розрахунковий динамічний прогин плати під вібраціями
};

/**
 * @brief Опис міжплатного ярусу кріплення (дистанційні стійки між двома сусідніми платами).
 */
struct StandoffTierConfig {
    double standoff_height_mm{10.0};        ///< Висота обраної стійки (мм)
    StandoffThread thread{StandoffThread::M3}; ///< Типорозмір різьби
    StandoffMaterial material{StandoffMaterial::BrassCW614N}; ///< Матеріал стійки
    double required_air_gap_mm{1.0};       ///< Нормативний повітряний зазор безпеки (мм)
};
