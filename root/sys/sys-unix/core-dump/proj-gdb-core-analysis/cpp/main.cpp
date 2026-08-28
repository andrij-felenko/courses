#include <iostream>
#include <vector>
#include <thread>
#include <memory>
#include <chrono>

struct PacketHeader {
    uint32_t magic;
    uint32_t payload_len;
    char* payload_ptr;
};

void process_packet(std::shared_ptr<PacketHeader> pkt, int thread_id) {
    // Невелика затримка для імітації паралельної роботи
    std::this_thread::sleep_for(std::chrono::milliseconds(50 * thread_id));
    
    if (thread_id == 2) {
        // Штучна помилка: обнуляємо вказівник у 2-му потоці без синхронізації
        pkt->payload_ptr = nullptr;
    }
    
    // Спроба зчитати дані за вказівником викликає SIGSEGV у 2-му або суміжних потоках
    std::cout << "Thread " << thread_id 
              << " byte: " << static_cast<int>(pkt->payload_ptr[0]) 
              << std::endl;
}

int main() {
    char data_buffer[] = "CRASH_DATA_PAYLOAD";
    auto pkt = std::make_shared<PacketHeader>();
    pkt->magic = 0xDEADBEEF;
    pkt->payload_len = sizeof(data_buffer);
    pkt->payload_ptr = data_buffer;

    std::vector<std::thread> workers;
    for (int i = 1; i <= 4; ++i) {
        workers.emplace_back(process_packet, pkt, i);
    }

    for (auto& t : workers) {
        if (t.joinable()) {
            t.join();
        }
    }
    return 0;
}
