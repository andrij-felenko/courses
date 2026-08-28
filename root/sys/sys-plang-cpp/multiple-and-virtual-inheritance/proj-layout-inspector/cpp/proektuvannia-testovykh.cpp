#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <numeric>
#include <string_view>
#include <vector>

// ── 1. Невіртуальна ієрархія ──────────────────────────────────────────────
struct Device {
    std::uint32_t device_id{0x11111111};
    virtual ~Device() = default;
    virtual void ping() {
        std::cout << "  [Device::ping] id=0x" << std::hex << device_id << '\n';
    }
};

struct AudioIn : public Device {
    std::uint32_t sample_rate{48000};
    void ping() override {
        std::cout << "  [AudioIn::ping] rate=" << std::dec << sample_rate << '\n';
    }
    virtual void read_samples() {
        std::cout << "  [AudioIn::read_samples]\n";
    }
};

struct AudioOut : public Device {
    std::uint32_t buffer_size{1024};
    void ping() override {
        std::cout << "  [AudioOut::ping] buf=" << std::dec << buffer_size << '\n';
    }
    virtual void write_samples() {
        std::cout << "  [AudioOut::write_samples]\n";
    }
};

struct AudioDuplexNV : public AudioIn, public AudioOut {
    std::uint32_t duplex_flags{0xAABBCCDD};
    void ping() override {
        std::cout << "  [AudioDuplexNV::ping] full duplex\n";
    }
};

// ── 2. Віртуальна ієрархія ────────────────────────────────────────────────
struct VDevice {
    std::uint32_t device_id{0x22222222};
    virtual ~VDevice() = default;
    virtual void ping() {
        std::cout << "  [VDevice::ping] id=0x" << std::hex << device_id << '\n';
    }
    virtual void identify() {
        std::cout << "  [VDevice::identify] base\n";
    }
};

struct VirtualAudioIn : virtual public VDevice {
    std::uint32_t sample_rate{96000};

    VirtualAudioIn() {
        // Дослідження vptr під час конструювання проміжного підоб'єкта
    }

    void ping() override {
        std::cout << "  [VirtualAudioIn::ping] rate=" << std::dec << sample_rate << '\n';
    }
    void identify() override {
        std::cout << "  [VirtualAudioIn::identify] in-branch\n";
    }
    virtual void read_samples() {
        std::cout << "  [VirtualAudioIn::read_samples]\n";
    }
};

struct VirtualAudioOut : virtual public VDevice {
    std::uint32_t buffer_size{2048};
    void ping() override {
        std::cout << "  [VirtualAudioOut::ping] buf=" << std::dec << buffer_size << '\n';
    }
    void identify() override {
        std::cout << "  [VirtualAudioOut::identify] out-branch\n";
    }
    virtual void write_samples() {
        std::cout << "  [VirtualAudioOut::write_samples]\n";
    }
};

struct AudioDuplexV : public VirtualAudioIn, public VirtualAudioOut {
    std::uint32_t duplex_flags{0x55667788};

    // Найбільш похідний клас безпосередньо ініціалізує віртуальну базу
    AudioDuplexV() : VDevice(), VirtualAudioIn(), VirtualAudioOut() {}

    void ping() override {
        std::cout << "  [AudioDuplexV::ping] unified virtual duplex\n";
    }
    void identify() override {
        std::cout << "  [AudioDuplexV::identify] most derived\n";
    }
};
