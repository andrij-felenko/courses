#pragma once

#include <cmath>
#include <string>
#include <string_view>

/**
 * @brief Базовий абстрактний клас кінематичного вузла тертя 3D-принтера.
 */
class FrictionNode {
public:
    virtual ~FrictionNode() = default;

    [[nodiscard]] virtual std::string_view getName() const noexcept = 0;
    [[nodiscard]] virtual double getContactAreaMm2() const noexcept = 0;
    [[nodiscard]] virtual double getGreaseRemainingPercent() const noexcept = 0;
    [[nodiscard]] virtual double calculateRequiredGreaseVolumeMl() const noexcept = 0;
    [[nodiscard]] virtual bool isMaintenanceRequired() const noexcept = 0;

    virtual void recordMovement(double distance_mm, double speed_mm_s) = 0;
    virtual void performService() = 0;

    [[nodiscard]] double getTotalTravelMeters() const noexcept { return total_travel_m_; }
    [[nodiscard]] double getCurrentFilmThicknessUm() const noexcept { return current_film_um_; }

protected:
    double total_travel_m_{0.0};
    double current_film_um_{10.0};     // Початкова товщина плівки SI-180 (мкм)
    double dust_contamination_{0.0};   // Відносний рівень пилу 0.0 .. 1.0
};

/**
 * @brief Модель гвинтової пари ходового гвинта T8 (трапецеїдальна нарізь).
 */
class LeadScrewNode final : public FrictionNode {
public:
    enum class NutMaterial { POM, Brass };

    LeadScrewNode(std::string name, NutMaterial material, double lead_mm = 8.0, double diameter_mm = 8.0)
        : name_(std::move(name)), material_(material), lead_mm_(lead_mm), diameter_mm_(diameter_mm) {
        // Кут підйому нарізі gamma = arctan(lead / (pi * d_m))
        double mean_d = diameter_mm_ - 1.0;
        lead_angle_rad_ = std::atan(lead_mm_ / (3.1415926535 * mean_d));
    }

    [[nodiscard]] std::string_view getName() const noexcept override { return name_; }

    [[nodiscard]] double getContactAreaMm2() const noexcept override {
        // Розрахункова площа взаємного контакту витків T8 та гайки (довжина 15 мм)
        return 380.0; 
    }

    void recordMovement(double distance_mm, double speed_mm_s) override {
        if (distance_mm <= 0.0) return;

        // Шлях ковзання витка по витку довший за лінійний крок: s_helical = s_linear / sin(gamma)
        double helical_dist_mm = distance_mm / std::sin(lead_angle_rad_);
        double helical_dist_m = helical_dist_mm / 1000.0;
        total_travel_m_ += distance_mm / 1000.0;

        // Деградація плівки залежно від матеріалу та швидкості
        double degradation_rate = (material_ == NutMaterial::POM) ? 0.00004 : 0.00008;
        double speed_factor = (speed_mm_s > 0.0) ? (speed_mm_s / 10.0) : 1.0;
        double film_loss = helical_dist_m * degradation_rate * speed_factor;

        current_film_um_ = std::max(0.5, current_film_um_ - film_loss);
        dust_contamination_ = std::min(1.0, dust_contamination_ + (helical_dist_m / 400.0) * 0.8);
    }

    [[nodiscard]] double getGreaseRemainingPercent() const noexcept override {
        double film_ratio = current_film_um_ / 10.0;
        double cleanliness = 1.0 - dust_contamination_;
        return std::max(0.0, std::min(100.0, (film_ratio * 0.6 + cleanliness * 0.4) * 100.0));
    }

    [[nodiscard]] double calculateRequiredGreaseVolumeMl() const noexcept override {
        // Об'єм змазки для створення плівки 12 мкм на гвинті T8 робочої довжини 300 мм
        // V = S_surface * h_film * k_reserve
        return 0.15; // 0.15 мл на один гвинт
    }

    [[nodiscard]] bool isMaintenanceRequired() const noexcept override {
        return (current_film_um_ <= 3.0) || (dust_contamination_ >= 0.75) || (total_travel_m_ >= 350.0);
    }

    void performService() override {
        current_film_um_ = 10.0;
        dust_contamination_ = 0.0;
        total_travel_m_ = 0.0;
    }

private:
    std::string name_;
    NutMaterial material_;
    double lead_mm_;
    double diameter_mm_;
    double lead_angle_rad_;
};

/**
 * @brief Модель лінійної рейкової напрямної (наприклад MGN9/MGN12) або циліндричного вала.
 */
class LinearRailNode final : public FrictionNode {
public:
    LinearRailNode(std::string name, double rail_length_mm)
        : name_(std::move(name)), rail_length_mm_(rail_length_mm) {}

    [[nodiscard]] std::string_view getName() const noexcept override { return name_; }

    [[nodiscard]] double getContactAreaMm2() const noexcept override {
        return 220.0; // Площа доріжок кочення каретки
    }

    void recordMovement(double distance_mm, double speed_mm_s) override {
        if (distance_mm <= 0.0) return;

        double dist_m = distance_mm / 1000.0;
        total_travel_m_ += dist_m;

        // У рейках кульки циркулюють, витіснення мастила залежить від швидкості
        double speed_factor = (speed_mm_s > 0.0) ? (speed_mm_s / 100.0) : 1.0;
        double film_loss = dist_m * 0.000025 * speed_factor;

        current_film_um_ = std::max(0.8, current_film_um_ - film_loss);
        dust_contamination_ = std::min(1.0, dust_contamination_ + (dist_m / 800.0) * 0.7);
    }

    [[nodiscard]] double getGreaseRemainingPercent() const noexcept override {
        double film_ratio = current_film_um_ / 10.0;
        double cleanliness = 1.0 - dust_contamination_;
        return std::max(0.0, std::min(100.0, (film_ratio * 0.5 + cleanliness * 0.5) * 100.0));
    }

    [[nodiscard]] double calculateRequiredGreaseVolumeMl() const noexcept override {
        return 0.10; // 0.10 мл у внутрішні канали каретки
    }

    [[nodiscard]] bool isMaintenanceRequired() const noexcept override {
        return (current_film_um_ <= 2.5) || (dust_contamination_ >= 0.8) || (total_travel_m_ >= 600.0);
    }

    void performService() override {
        current_film_um_ = 10.0;
        dust_contamination_ = 0.0;
        total_travel_m_ = 0.0;
    }

private:
    std::string name_;
    double rail_length_mm_;
};
