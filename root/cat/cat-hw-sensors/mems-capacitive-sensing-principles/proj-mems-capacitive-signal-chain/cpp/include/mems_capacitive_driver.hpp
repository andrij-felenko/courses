#pragma once

#include "mems_hardware_adapter.hpp"
#include <cstddef>
#include <cstdint>

namespace mems {

/**
 * @brief Режим фазової демодуляції сигналу несучої.
 */
enum class DemodulationMode {
    SynchronousInPhase,  ///< Синхронне помноження в фазі (0° -> +1, 180° -> -1)
    SynchronousInverted  ///< Інвертоване синхронне помноження (0° -> -1, 180° -> +1)
};

/**
 * @brief Статус виконання процедури автоматичного калібрування baseline.
 */
enum class CalibrationStatus {
    NotCalibrated,          ///< Калібрування ще не проводилося
    InProgress,             ///< Триває збір вибірок калібрування
    Success,                ///< Калібрування успішно завершено
    ErrorInvalidSamples,    ///< Некоректні параметри вибірки
    ErrorHardwareFault,     ///< Апаратний збій під час калібрування
    ErrorDriftExceeded      ///< Зсув baseline перевищує безпечний допуск
};

/**
 * @brief Структура конфігурації вимірювального тракту MEMS.
 */
struct CapacitiveSensingConfig {
    uint32_t excitation_freq_hz{100000};    ///< Частота збудження носія (100 кГц)
    std::size_t calibration_samples{256};    ///< Кількість вибірок для аналізу baseline
    float lpf_alpha{0.05f};                  ///< Коефіцієнт згладжування цифрового ФНЧ (0 < alpha <= 1)
    float sensitivity_pf_per_volt{1.5f};     ///< Масштабний коефіцієнт: pF на Вольт
    float scale_factor_um_per_pf{2.0f};      ///< Чутливість MEMS: мікрометри на pF
    float max_allowed_baseline_drift_v{0.6f};///< Максимально припустимий зсув нульового рівня (В)
};

/**
 * @brief Драйвер вимірювального тракту ємнісного MEMS-давача.
 *
 * Виконує фазову синхронну демодуляцію високочастотного носія,
 * автоматичне калібрування zero-offset baseline для нівелювання паразитичних ємностей
 * і температурного дрейфу, а також цифрову фільтрацію низьких частот (ФНЧ).
 */
class MemsCapacitiveDriver {
public:
    /**
     * @brief Конструктор драйвера.
     * @param hw_adapter Посилання на апаратний адаптер периферії МК.
     * @param config Структура з налаштуваннями вимірювального тракту.
     */
    explicit MemsCapacitiveDriver(IMemsHardwareAdapter& hw_adapter,
                                  CapacitiveSensingConfig config = CapacitiveSensingConfig{});

    /**
     * @brief Ініціалізує апаратне збудження та внутрішній стан драйвера.
     * @return true, якщо ініціалізація пройшла успішно.
     */
    bool initialize();

    /**
     * @brief Виконує автоматичне калібрування початкового стану нульового зсуву (baseline).
     *
     * На накопичених вибірках у стані спокою розраховує постійну складову (паразитичну ємність)
     * та зберігає baseline offset для подальшого віднімання від корисного сигналу.
     * @return Результат процедури калібрування.
     */
    CalibrationStatus calibrate_baseline();

    /**
     * @brief Обробляє поточну вибірку з АЦП: проводити демодуляцію та ФНЧ.
     * @return Відфільтрована напруга з урахуванням компенсації baseline (В).
     */
    float process_sample();

    /**
     * @brief Повертає розраховану зміну ємності MEMS-структури.
     * @return Зміна ємності delta C у пікофарадах (pF).
     */
    float get_capacitance_delta_pf() const noexcept;

    /**
     * @brief Повертає розрахований мікромеханічний зсув рухомих обкладок.
     * @return Зсув у мікрометрах (мкм / um).
     */
    float get_displacement_um() const noexcept;

    /**
     * @brief Повертає значення збереженого початкового зсуву baseline.
     * @return Зсув нульового рівня у Вольтах.
     */
    float get_baseline_offset_v() const noexcept;

    /**
     * @brief Повертає поточний статус калібрування.
     */
    CalibrationStatus get_calibration_status() const noexcept;

    /**
     * @brief Змінює режим фазової демодуляції.
     */
    void set_demodulation_mode(DemodulationMode mode) noexcept;

    /**
     * @brief Оновлює коефіцієнт цифрового фільтра низьких частот.
     * @param alpha Новий коефіцієнт згладжування (від 0.001 до 1.0).
     */
    void set_lpf_alpha(float alpha);

    /**
     * @brief Повертає останнє сире значення напруги з АЦП.
     */
    float get_last_raw_voltage() const noexcept;

    /**
     * @brief Повертає останнє демодульоване значення напруги (до ФНЧ).
     */
    float get_last_demodulated_voltage() const noexcept;

    /**
     * @brief Повертає останню відфільтровану напругу.
     */
    float get_last_filtered_voltage() const noexcept;

private:
    IMemsHardwareAdapter& hw_adapter_;
    CapacitiveSensingConfig config_;

    DemodulationMode demod_mode_{DemodulationMode::SynchronousInPhase};
    CalibrationStatus calibration_status_{CalibrationStatus::NotCalibrated};

    bool initialized_{false};
    float baseline_offset_v_{0.0f};
    float filter_state_v_{0.0f};

    float last_raw_v_{0.0f};
    float last_demod_v_{0.0f};
    float last_filtered_v_{0.0f};
};

} // namespace mems
