#include <iostream>
#include <cstdint>
#include <string_view>
#include <vector>
#include <array>
#include <bitset>
#include <iomanip>

namespace benchtop {

inline constexpr float kNoiseThresholdDps = 5.0f;

struct DiagnosticFlag {
    uint8_t bitIndex;
    std::string_view name;
    std::string_view description;
    std::string_view remedy;
};

inline constexpr std::array<DiagnosticFlag, 24> kBenchFlags = {{
    {0,  "NO_GYRO",         "Апаратний збій давача гіроскопа на шині SPI", "Перевірити пайку IMU та стабілізатор 3.3V"},
    {1,  "FAILSAFE",        "Активний аварійний режим Failsafe",           "Увімкнути радіопульт, перевірити живлення RX"},
    {2,  "RX_FAILSAFE",     "Приймач повідомляє про втрату зв'язку",       "Відновити радіолінк передавача з приймачем"},
    {3,  "BAD_RX_RECOVERY", "Триває захисна затримка поновлення сигналу",  "Зачекати 1 секунду стабільного зв'язку"},
    {4,  "BOXFAILSAFE",     "Активовано AUX-перемикач аварійного Failsafe", "Опустити тумблер Failsafe на апаратурі"},
    {5,  "THROTTLE",        "Стік газу перевищує безпечний нуль (min_check)","Опустити стік газу в крайнє нижнє положення"},
    {6,  "CLI",             "Контролер утримується в режимі CLI термінала", "Ввести команду exit або закрити термінал"},
    {7,  "CMS_MENU",        "Відкрито конфігураційне OSD меню",             "Закрити екранне меню налаштування"},
    {8,  "OSD_MENU",        "Активне службове меню телеметрії",           "Вийти зі службового графічного інтерфейсу"},
    {9,  "ROLLPITCH_CLIP",  "Канали крену/тангажу за межами 1000..2000 мкс", "Відкалібрувати діапазони стіків на пульті"},
    {10, "SERVO_INIT",      "Триває калібрування сервоприводів",           "Дочекатися закінчення стартового тесту"},
    {11, "MOTOR_PROTOCOL",  "Конфлікт таймерів виходу або протоколу ESC",  "Перевірити вибір DShot та ресурсів таймерів"},
    {12, "ACC_CAL",         "Акселерометр не має збереженого калібрування","Провести 6-осьове калібрування акселерометра"},
    {13, "MOTOR_TEST",      "Увімкнено стендовий режим повзунків моторів",  "Вимкнути тестування моторів у конфігураторі"},
    {14, "ARM_SWITCH",      "Тумблер Arming увімкнено до старту плати",     "Перевести тумблер Arming у позицію Disarm"},
    {15, "MSP",             "USB-конфігуратор утримує монопольний зв'язок","Від'єднатися від конфігуратора"},
    {16, "PARALYZE",        "Активовано аварійний режим Crash Paralyze",    "Перезавантажити живлення польотного стека"},
    {17, "GPS",             "GPS-Rescue блокує старт без 3D Fix супутників","Зняти прапорець вимагання GPS для столу"},
    {18, "RESC",            "Активовано тумблер повернення додому",        "Вимкнути режим Rescue на пульті"},
    {19, "RPMFILTER",       "Відсутній зв'язок двостороннього DShot RPM",  "Подати живлення на ESC від силового акумулятора"},
    {20, "REBOOT_REQUIRED", "Змінені налаштування вимагають рестарту",      "Виконати команду save або reboot"},
    {21, "NOPREARM",        "Не активовано захисну клавішу Prearm",        "Затиснути запобіжний тумблер Prearm"},
    {22, "LOAD",            "Перевантаження ядра процесора (CPU > 75%)",   "Знизити частоту циклу PID loop"},
    {23, "CALIBRATING",     "Триває стартове усереднення нуля гіроскопа",  "Забезпечити нерухомість дрона на столі"}
}};

class BenchSafetyValidator {
public:
    explicit BenchSafetyValidator(uint32_t rawMask) : rawMask_(rawMask), bits_(rawMask) {}

    [[nodiscard]] bool isReadyToArm() const noexcept {
        return bits_.none();
    }

    [[nodiscard]] std::vector<DiagnosticFlag> getActiveBlockers() const {
        std::vector<DiagnosticFlag> blockers;
        for (const auto& item : kBenchFlags) {
            if (bits_.test(item.bitIndex)) {
                blockers.push_back(item);
            }
        }
        return blockers;
    }

    void printDetailedReport() const {
        std::cout << "\n=======================================================\n";
        std::cout << "     СТЕНДОВИЙ ЗВІТ ГОТОВНОСТІ ДО АРМІНГУ (PRE-ARM)    \n";
        std::cout << "=======================================================\n";
        std::cout << "Бітова маска прапорців: 0x" << std::hex << std::uppercase
                  << std::setfill('0') << std::setw(8) << rawMask_ << std::dec << "\n";

        if (isReadyToArm()) {
            std::cout << "СТАТУС: [ УСПІХ ] Усі блокування знято. Армінг дозволено.\n";
        } else {
            const auto blockers = getActiveBlockers();
            std::cout << "СТАТУС: [ ЗАБЛОКОВАНО ] Виявлено активних перешкод: " << blockers.size() << "\n";
            std::cout << "-------------------------------------------------------\n";
            std::cout << "Деталізація блокувань:\n";

            for (const auto& b : blockers) {
                std::cout << "  [!] Біт " << std::setw(2) << static_cast<int>(b.bitIndex)
                          << ": " << std::left << std::setw(16) << b.name << " | " << b.description << "\n"
                          << "      ДІЯ: " << b.remedy << "\n";
            }
        }
        std::cout << "=======================================================\n\n";
    }

    [[nodiscard]] static bool verifyPidNegativeFeedback(float gyroRateDps, float deltaMotorThrottle) noexcept {
        if (gyroRateDps > kNoiseThresholdDps && deltaMotorThrottle > 0.01f) {
            return true;
        }
        if (gyroRateDps < -kNoiseThresholdDps && deltaMotorThrottle < -0.01f) {
            return true;
        }
        return false;
    }

private:
    uint32_t rawMask_;
    std::bitset<32> bits_;
};

} // namespace benchtop
