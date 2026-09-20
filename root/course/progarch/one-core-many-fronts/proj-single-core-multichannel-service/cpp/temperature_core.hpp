#pragma once

#include <chrono>
#include <expected>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>

// ============================================================================
// ДОМЕННІ ПОМИЛКИ
// ============================================================================

/// @brief Доменні коди помилок при зміні температури кліматичної зони.
/// Ядро оперує виключно цими поняттями і не знає про HTTP-коди чи сигнали брокера.
enum class DomainError {
    InvalidCommand,         ///< Некоректні вхідні параметри команди
    ZoneNotFound,           ///< Кліматична зона не існує в системі
    AccessDenied,           ///< Користувач не має прав на зміну параметрів зони
    TemperatureOutOfRange,  ///< Температура виходить за межі допустимого діапазону зони
    DeviceBusy              ///< Апаратний термостат тимчасово зайнятий або недоступний
};

/// @brief Текстовий опис доменної помилки для логування та діагностики.
[[nodiscard]] constexpr std::string_view to_string(DomainError error) noexcept {
    switch (error) {
        case DomainError::InvalidCommand:
            return "InvalidCommand (Некоректні параметри команди)";
        case DomainError::ZoneNotFound:
            return "ZoneNotFound (Кліматичну зону не знайдено)";
        case DomainError::AccessDenied:
            return "AccessDenied (Відмовлено в доступі для вказаного користувача)";
        case DomainError::TemperatureOutOfRange:
            return "TemperatureOutOfRange (Цільова температура виходить за межі безпеки зони)";
        case DomainError::DeviceBusy:
            return "DeviceBusy (Апаратний контролер зони тимчасово зайнятий)";
    }
    return "UnknownError";
}

// ============================================================================
// НЕЗМІННИЙ ОБ'ЄКТ ПЕРЕДАЧІ ДАНИХ (COMMAND DTO) ТА РЕЗУЛЬТАТ
// ============================================================================

/// @brief Незмінний Command DTO, що передається через вхідний порт у ядро.
/// Захищає ядро від залежностей на структури зовнішніх протоколів (JSON, CLI flags тощо).
class SetTemperatureCommand {
public:
    SetTemperatureCommand(std::string zone_id, double target_temperature, std::string user_id)
        : zone_id_(std::move(zone_id)),
          target_temperature_(target_temperature),
          user_id_(std::move(user_id)) {}

    [[nodiscard]] const std::string& zone_id() const noexcept { return zone_id_; }
    [[nodiscard]] double target_temperature() const noexcept { return target_temperature_; }
    [[nodiscard]] const std::string& user_id() const noexcept { return user_id_; }

private:
    std::string zone_id_;
    double target_temperature_{0.0};
    std::string user_id_;
};

/// @brief Структура успішного результату виконання сценарію зміни температури.
struct TemperatureResult {
    std::string zone_id;
    double new_temperature{0.0};
    double previous_temperature{0.0};
    std::chrono::system_clock::time_point timestamp;
};

// ============================================================================
// АБСТРАКТНИЙ ІНТЕРФЕЙС ВХІДНОГО ПОРТУ (USE CASE)
// ============================================================================

/// @brief Вхідний порт (Driving/Inbound Port) для сценарію регулювання температури.
/// Визначає контракт виконання бізнес-сценарію без прив'язки до деталей транспорту чи середовища.
class ISetTemperatureUseCase {
public:
    virtual ~ISetTemperatureUseCase() = default;

    /// @brief Виконати сценарій зміни цільової температури.
    /// @param command Незмінний DTO команди.
    /// @return std::expected з успішним результатом або типізованою доменною помилкою.
    [[nodiscard]] virtual std::expected<TemperatureResult, DomainError> 
    execute(const SetTemperatureCommand& command) = 0;
};

// ============================================================================
// СЕРВІС ПРИКЛАДНОГО ЯДРА (APPLICATION CORE)
// ============================================================================

/// @brief Внутрішній стан кліматичної зони в межах доменного ядра.
struct ClimateZone {
    std::string id;
    double current_temperature{20.0};
    double min_temperature{15.0};
    double max_temperature{30.0};
    std::string authorized_user; // Дозволений оператор зони (або "admin")
    bool is_busy{false};         // Прапорець апаратної зайнятості для симуляції збоїв
};

/// @brief Реалізація прикладного ядра: централізовано виконує бізнес-правила
/// та інваріанти незалежно від того, через який адаптер надійшов запит.
class TemperatureControlService : public ISetTemperatureUseCase {
public:
    TemperatureControlService();

    /// @brief Зареєструвати кліматичну зону з її граничними параметрами.
    void register_zone(std::string id, double current_temp, double min_temp, 
                       double max_temp, std::string authorized_user);

    /// @brief Встановити прапорець апаратної зайнятості для симуляції транзієнтних збоїв.
    void set_zone_busy(const std::string& zone_id, bool busy);

    /// @brief Отримати поточну температуру зони (для діагностики).
    [[nodiscard]] std::optional<double> get_temperature(const std::string& zone_id) const;

    /// @brief Реалізація вхідного порту: виконання сценарію з перевіркою інваріантів.
    [[nodiscard]] std::expected<TemperatureResult, DomainError> 
    execute(const SetTemperatureCommand& command) override;

private:
    std::unordered_map<std::string, ClimateZone> zones_;
};
