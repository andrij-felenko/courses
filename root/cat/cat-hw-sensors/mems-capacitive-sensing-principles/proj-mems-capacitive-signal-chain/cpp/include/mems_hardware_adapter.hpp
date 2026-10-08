#pragma once

#include <cstdint>

namespace mems {

/**
 * @brief Фаза прямокутного сигналу збудження MEMS-структури.
 */
enum class ExcitationPhase {
    Phase0,   ///< Пряма фаза (0 градусів)
    Phase180  ///< Противофаза (180 градусів)
};

/**
 * @brief Абстрактний інтерфейс апаратного адаптера (HAL) для MEMS-зчитування.
 *
 * Надає доступ до таймерного керування противофазним збудженням,
 * компенсаційного ЦАП для зсуву та оцифрування аналогового відгуку з АЦП.
 */
class IMemsHardwareAdapter {
public:
    virtual ~IMemsHardwareAdapter() = default;

    /**
     * @brief Налаштування генерації противофазних сигналів збудження.
     * @param frequency_hz Частота несучого сигналу в Герцах.
     * @return true у разі успішного налаштування периферії.
     */
    virtual bool configure_excitation(uint32_t frequency_hz) = 0;

    /**
     * @brief Вмикає або вимикає генерацію збудження на обкладках MEMS.
     * @param enable Прапор активації.
     * @return true у разі успіху.
     */
    virtual bool set_excitation_enabled(bool enable) = 0;

    /**
     * @brief Встановлює компенсаційну напругу ЦАП для аналогового балансування.
     * @param volts Напруга компенсації в Вольтах.
     * @return true у разі успішного оновлення ЦАП.
     */
    virtual bool set_dac_offset_voltage(float volts) = 0;

    /**
     * @brief Зчитує миттєву напругу з підсилювача заряду через АЦП.
     * @return Напруга відгуку в Вольтах.
     */
    virtual float read_adc_voltage() = 0;

    /**
     * @brief Повертає поточну фазу збудження для фазової демодуляції.
     * @return Поточний стан фази несучої (Phase0 або Phase180).
     */
    virtual ExcitationPhase current_excitation_phase() const = 0;
};

} // namespace mems
