#include <new>
#include <memory>
#include <iostream>
#include <string>

struct Packet {
    int id;
    std::string payload;

    Packet(int i, std::string p) : id(i), payload(std::move(p)) {
        std::cout << "  Конструктор Packet #" << id << "\n";
    }

    ~Packet() {
        std::cout << "  Деструктор Packet #" << id << "\n";
    }
};

void lifecycle_demo() {
    // 1. Алокація сирої пам'яті під об'єкт (об'єкта ще немає)
    alignas(Packet) std::byte raw_storage[sizeof(Packet)];

    // 2. Ініціалізація: placement new викликає конструктор за вказаною адресою
    Packet* pkt = ::new (raw_storage) Packet(42, "Telemetry data");

    // 3. Час життя: об'єкт повністю валідний
    std::cout << "  Payload: " << pkt->payload << "\n";

    // 4. Деструкція: явний виклик деструктора (пам'ять raw_storage НЕ звільняється)
    pkt->~Packet();

    // 5. Деалокація: raw_storage автоматично зникає зі стека при виході
}
