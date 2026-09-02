#pragma once
// Транспорт: послідовний порт радіомодема плюс парсер кадрів MAVLink v1/v2.
#include <chrono>
#include <cstdint>
#include <map>
#include <string>
#include <vector>

#include <mavlink/v2.0/common/mavlink.h>

using Clock = std::chrono::steady_clock;

// Якість радіолінка рахуємо за циклічним лічильником seq у заголовку кадру:
// пропуск у нумерації означає кадр, який не долетів.
struct LinkStats {
    std::uint64_t received = 0;      // валідних кадрів зібрано
    std::uint64_t lost = 0;          // дірок у нумерації seq
    std::uint64_t sent = 0;          // кадрів віддано в порт
    std::uint32_t parse_errors = 0;  // биті CRC і сміття: перша ознака чужої швидкості UART

    double lossPercent() const;
};

enum class MavVersion { Unknown, V1, V2 };

class SerialLink {
public:
    SerialLink(const std::string& device, unsigned baud);
    ~SerialLink();
    SerialLink(const SerialLink&) = delete;
    SerialLink& operator=(const SerialLink&) = delete;

    // Забирає все, що встигло накопичитись у драйвері, і повертає зібрані кадри.
    // Не блокує: порожній вектор — нормальний результат.
    std::vector<mavlink_message_t> receive();
    void send(const mavlink_message_t& msg);

    MavVersion version() const { return version_; }
    const LinkStats& stats() const { return stats_; }
    void resetStatsWindow();  // вікно для оцінки втрат за останні секунди

private:
    void lockVersion(std::uint8_t magic);
    void trackSeq(const mavlink_message_t& msg);

    int fd_ = -1;
    MavVersion version_ = MavVersion::Unknown;
    LinkStats stats_{};
    std::map<std::uint16_t, std::uint8_t> last_seq_;  // ключ: (sysid << 8) | compid
};
