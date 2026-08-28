#include <iostream>
#include <string_view>
#include <array>
#include <optional>
#include <format>

enum class FaultCode : uint8_t {
    None = 0,
    SupplyUndervoltage = 1,
    Rs485NoTermination = 2,
    SensorOpenCircuit  = 3,
    ConfigCrcMismatch  = 4
};

struct FaultDescriptor {
    FaultCode code;
    std::string_view blink_pattern;
    std::string_view symptom;
    std::string_view probable_cause;
    std::string_view corrective_action;
};

class DiagnosticsManager {
public:
    static constexpr std::array<FaultDescriptor, 4> FaultRegistry{{
        {
            FaultCode::SupplyUndervoltage,
            "* _ _ _ _ (1 спалах, пауза 1.5 с)",
            "STATUS LED блимає 1 раз кожні 2 секунди",
            "Напруга живлення впала нижче 18 В під навантаженням",
            "Перевірити перетин кабелю живлення та вихідну напругу блока 24 В DC"
        },
        {
            FaultCode::Rs485NoTermination,
            "* * _ _ _ (2 спалахи, пауза 1.5 с)",
            "STATUS LED блимає 2 рази кожні 2 секунди",
            "Опір знеструмленої лінії RS-485 відрізняється від 60 Ом (немає термінатора)",
            "Увімкнути DIP-перемикач TERM 120R на першому та останньому вузлах шини"
        },
        {
            FaultCode::SensorOpenCircuit,
            "* * * _ _ (3 спалахи, пауза 1.5 с)",
            "STATUS LED блимає 3 рази кожні 2 секунди",
            "Струм у петлі 4-20 мА становить 0.0 мА (обрив сигнального кабелю)",
            "Перевірити цілісність лінії від клемника SENSOR+ до первинного перетворювача"
        },
        {
            FaultCode::ConfigCrcMismatch,
            "* * * * _ (4 спалахи, пауза 1.5 с)",
            "STATUS LED блимає 4 рази кожні 2 секунди",
            "Контрольна сума CRC32 налаштувань у пам'яті FRAM не збігається",
            "Скинути прилад до заводських налаштувань утримуванням кнопки RESET 10 с"
        }
    }};

    [[nodiscard]] static constexpr std::optional<FaultDescriptor> lookup(FaultCode code) noexcept {
        for (const auto& item : FaultRegistry) {
            if (item.code == code) {
                return item;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] static FaultCode evaluate_hardware(float v_supply, float bus_res_ohms,
                                                     bool sensor_ok, bool crc_ok) noexcept {
        if (v_supply < 18.0f) return FaultCode::SupplyUndervoltage;
        if (bus_res_ohms < 45.0f || bus_res_ohms > 75.0f) return FaultCode::Rs485NoTermination;
        if (!sensor_ok) return FaultCode::SensorOpenCircuit;
        if (!crc_ok) return FaultCode::ConfigCrcMismatch;
        return FaultCode::None;
    }

    static void emit_service_report(FaultCode code) {
        auto fault = lookup(code);
        if (!fault) {
            std::cout << "[СИСТЕМА]: Самодіагностика POST завершена без зауважень.\n";
            return;
        }

        std::cout << "\n=======================================================\n";
        std::cout << "АВАРІЙНИЙ ПРОТОКОЛ ЛОКАЛІЗАЦІЇ ВІДМОВИ (C++20 Engine)\n";
        std::cout << "=======================================================\n";
        std::cout << std::format("[КОД ПОМИЛКИ] : #{}\n", static_cast<uint32_t>(fault->code));
        std::cout << std::format("[СВІТЛОДІОД]   : {}\n", fault->blink_pattern);
        std::cout << std::format("[СИМПТОМ]     : {}\n", fault->symptom);
        std::cout << std::format("[ПРИЧИНА]     : {}\n", fault->probable_cause);
        std::cout << std::format("[ІНСТРУКЦІЯ]  : {}\n", fault->corrective_action);
        std::cout << "=======================================================\n";
    }
};

int main() {
    std::cout << "Запуск Power-On Self-Test промислового контролера...\n";

    // Симуляція відмови термінації шини (опір 120 Ом замість еквівалентних 60 Ом)
    auto fault = DiagnosticsManager::evaluate_hardware(24.0f, 120.0f, true, true);
    DiagnosticsManager::emit_service_report(fault);

    return 0;
}
