#include <iostream>
#include <span>
#include <vector>
#include <cstdint>
#include <stdexcept>

// Низькорівневий драйвер апаратного каналу зв'язку
class HardwareChannelBase {
public:
    void open_channel(uint32_t channel_id, uint32_t baud_rate) {
        std::cout << "Hardware: відкрито канал #" << channel_id << " на швидкості " << baud_rate << " бод.\n";
        is_active_ = true;
    }

    void close_channel() noexcept {
        std::cout << "Hardware: канал закрито.\n";
        is_active_ = false;
    }

    bool is_active() const noexcept {
        return is_active_;
    }

    // Небезпечний низькорівневий метод прямого запису в регістри:
    void direct_register_write(uint32_t reg_offset, uint32_t raw_value) {
        std::cout << "Hardware: прямий запис у регістр 0x" << std::hex << reg_offset 
                  << " значення 0x" << raw_value << std::dec << '\n';
    }

    // Низькорівневе читання статусу з шини:
    uint32_t read_hardware_flags() const noexcept {
        return 0x00000001; // статус готовності
    }

protected:
    void raw_transmit_bytes(std::span<const uint8_t> data) {
        std::cout << "Hardware: передано " << data.size() << " байтів у фізичний канал.\n";
    }

private:
    bool is_active_{false};
};

// Високорівневий клієнтський драйвер для безпечної передачі пакетів
class SafePacketTransceiver : private HardwareChannelBase {
public:
    SafePacketTransceiver(uint32_t channel_id, uint32_t baud_rate) {
        open_channel(channel_id, baud_rate);
    }

    ~SafePacketTransceiver() {
        if (is_active()) {
            close_channel();
        }
    }

    // 1. Відкриваємо публічно безпечні методи перевірки та закриття:
    using HardwareChannelBase::is_active;
    using HardwareChannelBase::close_channel;

    // 2. Реалізуємо високорівневий безпечний метод відправлення з валідацією:
    void send_packet(std::span<const uint8_t> packet) {
        if (!is_active()) {
            throw std::runtime_error("Канал не активний для відправлення!");
        }
        if (packet.empty() || packet.size() > 1024) {
            throw std::invalid_argument("Некоректний розмір пакета (1..1024 байтів)!");
        }
        // Викликаємо protected-метод базового класу:
        raw_transmit_bytes(packet);
    }

    // Небезпечні методи direct_register_write та read_hardware_flags 
    // залишаються приватними й повністю недоступними для клієнтів SafePacketTransceiver!
};

int main() {
    SafePacketTransceiver transceiver(1, 115200);

    if (transceiver.is_active()) {
        std::cout << "Трансивер готовий до роботи.\n";
    }

    std::vector<uint8_t> payload = {0x01, 0x02, 0x03, 0x04};
    transceiver.send_packet(payload);

    // Спроба виклику низькорівневих операцій заблокована компілятором:
    // transceiver.direct_register_write(0x10, 0xFF); 
    // ^ Помилка: 'direct_register_write' is private within this context

    // transceiver.open_channel(2, 9600);
    // ^ Помилка: 'open_channel' is private within this context

    return 0;
}
