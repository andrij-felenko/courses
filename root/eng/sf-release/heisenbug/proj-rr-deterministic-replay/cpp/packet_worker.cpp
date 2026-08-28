// packet_worker.cpp
#include <iostream>
#include <vector>
#include <cstring>
#include <functional>
#include <random>

struct PacketContext {
    char header[8]{'P','K','T','_','H','D','R','\0'};
    std::function<void(const char*)> handler;
};

void default_logger(const char* msg) {
    std::cout << "[LOG] " << msg << "\n";
}

void parse_payload(const char* input, size_t len) {
    char local_buffer[16];
    // Потенційне пошкодження стек-фрейму при len > 16
    std::memcpy(local_buffer, input, len);
    local_buffer[15] = '\0';
}

void process_network_event(int event_id, std::mt19937& rng) {
    PacketContext ctx;
    ctx.handler = default_logger;

    std::uniform_int_distribution<size_t> dist(12, 27);
    size_t payload_len = dist(rng);

    char payload_data[32];
    std::memset(payload_data, 'A', sizeof(payload_data));

    parse_payload(payload_data, payload_len);

    if (event_id % 1000 == 0 && ctx.handler) {
        ctx.handler("Packet processed successfully.");
    }
}

int main() {
    std::mt19937 rng(42);
    std::cout << "[START] Processing network stream...\n";

    for (int i = 0; i < 50000; ++i) {
        process_network_event(i, rng);
    }

    std::cout << "[FINISH] All packets processed successfully.\n";
    return 0;
}
