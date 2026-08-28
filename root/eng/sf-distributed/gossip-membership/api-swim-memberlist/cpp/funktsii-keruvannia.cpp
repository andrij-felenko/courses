#include <memory>
#include <expected>
#include <string>
#include <span>

namespace swim {

class SwimCluster {
public:
    // Фабричний метод ініціалізації екземпляра
    static std::expected<std::unique_ptr<SwimCluster>, std::string> Create(const Config &config);

    virtual ~SwimCluster() = default;

    // Підключення до кластера через адресу сіда
    virtual std::expected<void, std::string> Join(uint32_t seed_ip, uint16_t seed_port) = 0;

    // Ітерація протокольного циклу (викликається в таймері або event-loop)
    virtual void Step() = 0;

    // Публікація прикладних пліток на весь кластер
    virtual std::expected<void, std::string> BroadcastUserMessage(std::span<const uint8_t> data) = 0;

    // Коректний вихід із кластера (Graceful shutdown)
    virtual void Leave() = 0;
};

} // namespace swim
