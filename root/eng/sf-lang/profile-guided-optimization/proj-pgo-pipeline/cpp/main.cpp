// main.cpp — Диспетчер мережевих пакетів мовою C++
#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <random>
#include <span>
#include <array>
#include <cstdint>

enum class PacketType : uint8_t {
    Data = 0,
    Control = 1,
    Corrupted = 2
};

struct Packet {
    PacketType type;
    uint32_t payload_len;
    std::array<uint8_t, 64> payload;
};

class IPacketProcessor {
public:
    virtual ~IPacketProcessor() = default;
    virtual uint64_t process(const Packet& pkt) const = 0;
};

class DataPacketProcessor final : public IPacketProcessor {
public:
    uint64_t process(const Packet& pkt) const override {
        uint64_t acc = 0;
        for (uint32_t i = 0; i < pkt.payload_len; ++i) {
            acc = (acc * 33) ^ pkt.payload[i];
        }
        return acc;
    }
};

class ControlPacketProcessor final : public IPacketProcessor {
public:
    uint64_t process(const Packet& pkt) const override {
        return static_cast<uint64_t>(pkt.payload_len) * 0x9e3779b97f4a7c15ULL;
    }
};

class CorruptedPacketProcessor final : public IPacketProcessor {
public:
    uint64_t process(const Packet& pkt) const override {
        // Холодний шлях: імітація складного логування
        std::cerr << "Log error: corrupted packet length " << pkt.payload_len << "\n";
        return 0;
    }
};

constexpr size_t TotalPackets = 5'000'000;

int main() {
    std::array<std::unique_ptr<IPacketProcessor>, 3> processors = {
        std::make_unique<DataPacketProcessor>(),
        std::make_unique<ControlPacketProcessor>(),
        std::make_unique<CorruptedPacketProcessor>()
    };

    std::vector<Packet> stream(TotalPackets);
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(0, 999);

    for (size_t i = 0; i < TotalPackets; ++i) {
        int r = dist(rng);
        if (r < 980) {
            stream[i].type = PacketType::Data;
            stream[i].payload_len = 32;
        } else if (r < 995) {
            stream[i].type = PacketType::Control;
            stream[i].payload_len = 16;
        } else {
            stream[i].type = PacketType::Corrupted;
            stream[i].payload_len = 4;
        }
        for (uint32_t j = 0; j < stream[i].payload_len; ++j) {
            stream[i].payload[j] = static_cast<uint8_t>(j + i);
        }
    }

    auto start = std::chrono::steady_clock::now();

    uint64_t total_checksum = 0;
    for (const auto& pkt : stream) {
        const auto& proc = processors[static_cast<size_t>(pkt.type)];
        // Віртуальний поліморфний виклик через vtable
        total_checksum += proc->process(pkt);
    }

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout << "Checksum: 0x" << std::hex << total_checksum << std::dec
              << ", Time: " << elapsed.count() << " s\n";

    return 0;
}
