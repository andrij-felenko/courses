#include <iostream>
#include <optional>
#include <string_view>

/* Типізоване представлення електричного потенціалу вузла */
enum class NodeLevel {
    StrongZero,   // Чистий 0 В (земля)
    StrongOne,    // Чиста напруга Vdd
    DegradedOne,  // Знижена одиниця Vdd - Vth
    DegradedZero  // Підвищений нуль |Vthp|
};

/* Ідіоматичний клас передавального вентиля */
class TransmissionGate {
public:
    constexpr TransmissionGate() = default;

    // Симуляція передачі сигналу крізь ключ
    [[nodiscard]] constexpr std::optional<NodeLevel> transfer(
        NodeLevel input, 
        bool enable
    ) const noexcept {
        if (!enable) {
            return std::nullopt; // Стан високого імпедансу (Hi-Z)
        }
        // Завдяки парі NMOS+PMOS сигнал проходить без порогової втрати
        return input;
    }

    // Для порівняння: модель одиночного NMOS-ключа
    [[nodiscard]] static constexpr std::optional<NodeLevel> singleNmosTransfer(
        NodeLevel input, 
        bool enable
    ) noexcept {
        if (!enable) {
            return std::nullopt;
        }
        if (input == NodeLevel::StrongOne) {
            return NodeLevel::DegradedOne; // Порогова втрата Vthn
        }
        return input;
    }
};

constexpr std::string_view levelToString(std::optional<NodeLevel> lvl) noexcept {
    if (!lvl.has_value()) return "Hi-Z (Високоімпедансний стан)";
    switch (*lvl) {
        case NodeLevel::StrongZero:   return "Сильний 0 (0.0 В)";
        case NodeLevel::StrongOne:    return "Сильна 1 (Vdd = 3.3 В)";
        case NodeLevel::DegradedOne:  return "Квола 1 (Vdd - Vth ≈ 2.5 В)";
        case NodeLevel::DegradedZero: return "Кволий 0 (|Vthp| ≈ 0.7 В)";
    }
    return "Невідомо";
}

int main() {
    constexpr TransmissionGate tg;

    std::cout << "--- Симуляція проходження рівнів крізь CMOS TG ---\n";
    std::cout << "Вхід StrongZero, EN=true -> " 
              << levelToString(tg.transfer(NodeLevel::StrongZero, true)) << '\n';
    std::cout << "Вхід StrongOne,  EN=true -> " 
              << levelToString(tg.transfer(NodeLevel::StrongOne, true)) << '\n';
    std::cout << "Вхід StrongOne,  EN=false -> " 
              << levelToString(tg.transfer(NodeLevel::StrongOne, false)) << '\n';

    std::cout << "\n--- Для порівняння: одиночний NMOS ключ ---\n";
    std::cout << "Вхід StrongOne,  EN=true -> " 
              << levelToString(TransmissionGate::singleNmosTransfer(NodeLevel::StrongOne, true)) << '\n';

    return 0;
}
