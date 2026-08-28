#ifndef DARCY_API_H
#define DARCY_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ── Фізичні константи перерахунку ───────────────────────────────────── */
#define DARCY_TO_M2         0.9869233e-12   /**< Переведення Дарсі в м² */
#define M2_TO_DARCY         1.0132501e12    /**< Переведення м² в Дарсі */
#define MILLIDARCY_TO_M2    0.9869233e-15   /**< Переведення мілідарсі в м² */
#define WATER_VISCOSITY_20C 1.002e-3        /**< Динамічна в'язкість води при 20°C (Па·с) */
#define WATER_DENSITY_20C   998.2           /**< Густина прісної води при 20°C (кг/м³) */
#define GRAVITY_ACCEL       9.80665         /**< Стандартне прискорення вільного падіння (м/с²) */

/* ── Структури даних ─────────────────────────────────────────────────── */

/**
 * @brief Термодинамічні властивості флюїду
 */
typedef struct {
    double viscosity;  /**< Динамічна в'язкість μ (Па·с) */
    double density;    /**< Густина ρ (кг/м³) */
} fluid_properties_t;

/**
 * @brief Анізотропний тензор проникності 3x3 у системі координат (м²)
 */
typedef struct {
    double kxx, kxy, kxz;
    double kyx, kyy, kyz;
    double kzx, kzy, kzz;
} permeability_tensor_t;

/**
 * @brief Трехвимірний вектор декартових координат або швидкостей
 */
typedef struct {
    double x, y, z;
} vector3d_t;

/* ── Інтерфейсні функції конвертації ─────────────────────────────────── */

static inline double darcy_to_m2(double darcy) {
    return darcy * DARCY_TO_M2;
}

static inline double m2_to_darcy(double m2) {
    return m2 * M2_TO_DARCY;
}

static inline double millidarcy_to_m2(double md) {
    return md * MILLIDARCY_TO_M2;
}

/**
 * @brief Обчислити коефіцієнт фільтрації K (м/с) за геометрією k (м²) та флюїдом
 */
static inline double permeability_to_hydraulic_cond(double k_m2, const fluid_properties_t *fluid) {
    if (!fluid || fluid->viscosity <= 0.0) return 0.0;
    return (k_m2 * fluid->density * GRAVITY_ACCEL) / fluid->viscosity;
}

/* ── Обчислювальний ядерний інтерфейс ────────────────────────────────── */

/**
 * @brief Скалярний розрахунок об'ємної витрати Дарсі Q (м³/с) для одновимірного керна
 * @param area Площа поперечного перерізу зразка (м²)
 * @param permeability_m2 Внутрішня проникність k (м²)
 * @param length Довжина зразка L (м)
 * @param delta_p Перепад гідростатичного тиску Δp (Па)
 * @param fluid Параметри флюїду (в'язкість, густина)
 * @return Повна об'ємна витрата Q (м³/с)
 */
double darcy_compute_flow_rate(double area, double permeability_m2, double length,
                                double delta_p, const fluid_properties_t *fluid);

/**
 * @brief 3D векторний розрахунок швидкості фільтрації v_d для анізотропного пласта
 * @param tensor Тензор проникності породи k_ij (м²)
 * @param grad_p Градієнт тиску ∇p (Па/м)
 * @param fluid Параметри флюїду
 * @param include_gravity Враховувати гравітаційне поле (ρ g)
 * @return Вектор швидкості фільтрації v_d (м/с)
 */
vector3d_t darcy_compute_velocity_3d(const permeability_tensor_t *tensor,
                                      const vector3d_t *grad_p,
                                      const fluid_properties_t *fluid,
                                      bool include_gravity);

#ifdef __cplusplus
}
#endif

/* ── C++17 Об'єктно-орієнтований інтерфейс ──────────────────────────── */
#ifdef __cplusplus
namespace darcy {

/**
 * @brief Клас для представлення пористого середовища з контролем одиниць
 */
class PorousMedium {
public:
    constexpr PorousMedium(double k_m2, double porosity) noexcept
        : k_m2_(k_m2), porosity_(porosity) {}

    [[nodiscard]] static constexpr PorousMedium from_darcy(double k_darcy, double porosity) noexcept {
        return PorousMedium(k_darcy * DARCY_TO_M2, porosity);
    }

    [[nodiscard]] static constexpr PorousMedium from_millidarcy(double k_md, double porosity) noexcept {
        return PorousMedium(k_md * MILLIDARCY_TO_M2, porosity);
    }

    [[nodiscard]] constexpr double permeability_m2() const noexcept { return k_m2_; }
    [[nodiscard]] constexpr double permeability_darcy() const noexcept { return k_m2_ * M2_TO_DARCY; }
    [[nodiscard]] constexpr double porosity() const noexcept { return porosity_; }

    /**
     * @brief Розрахувати дійсну порову швидкість v_p за макроскопічною швидкістю Дарсі v_d
     */
    [[nodiscard]] constexpr double pore_velocity(double darcy_velocity) const noexcept {
        return (porosity_ > 0.0) ? (darcy_velocity / porosity_) : 0.0;
    }

    /**
     * @brief Оцінити проникність за формулою Кармана-Козені
     * @param grain_diameter_m Середній діаметр зерен (м)
     * @param porosity Пористість (0..1)
     */
    [[nodiscard]] static double estimate_kozeny_carman(double grain_diameter_m, double porosity) noexcept {
        if (porosity <= 0.0 || porosity >= 1.0) return 0.0;
        const double phi3 = porosity * porosity * porosity;
        const double one_minus_phi = 1.0 - porosity;
        return (grain_diameter_m * grain_diameter_m * phi3) / (180.0 * one_minus_phi * one_minus_phi);
    }

private:
    double k_m2_{0.0};
    double porosity_{0.0};
};

} // namespace darcy
#endif

#endif /* DARCY_API_H */
