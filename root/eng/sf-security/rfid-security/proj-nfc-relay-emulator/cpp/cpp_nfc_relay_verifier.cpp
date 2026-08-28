// cpp_nfc_relay_verifier.cpp - C++17 RAII & Chrono NFC Timing Verifier
#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <span>
#include <memory>
#include <cstdint>
#include <nfc/nfc.h>

// RAII обгортка для libnfc context та device
class NfcReader {
public:
    NfcReader() {
        nfc_init(&context_);
        if (!context_) {
            throw std::runtime_error("Failed to initialize libnfc context");
        }
        device_ = nfc_open(context_, nullptr);
        if (!device_) {
            nfc_exit(context_);
            throw std::runtime_error("Failed to open NFC device");
        }
        if (nfc_initiator_init(device_) < 0) {
            nfc_close(device_);
            nfc_exit(context_);
            throw std::runtime_error("Failed to set NFC initiator mode");
        }
    }

    ~NfcReader() {
        if (device_) nfc_close(device_);
        if (context_) nfc_exit(context_);
    }

    // Заборона копіювання
    NfcReader(const NfcReader&) = delete;
    NfcReader& operator=(const NfcReader&) = delete;

    struct ApduResult {
        std::vector<uint8_t> payload;
        std::chrono::microseconds rtt;
    };

    std::optional<ApduResult> sendApdu(std::span<const uint8_t> apdu) {
        std::vector<uint8_t> rx_buf(264);
        
        auto start = std::chrono::steady_clock::now();
        int res = nfc_initiator_transceive_bytes(device_, apdu.data(), apdu.size(),
                                                 rx_buf.data(), rx_buf.size(), -1);
        auto end = std::chrono::steady_clock::now();

        if (res < 0) {
            return std::nullopt;
        }

        rx_buf.resize(static_cast:size_t>(res));
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        return ApduResult{ std::move(rx_buf), duration };
    }

private:
    nfc_context* context_{nullptr};
    nfc_device* device_{nullptr};
};

int main() {
    constexpr std::chrono::microseconds kMaxAllowedRtt{15000}; // 15 ms

    try {
        NfcReader reader;
        
        const std::vector<uint8_t> select_aid = {
            0x00, 0xA4, 0x04, 0x00, 0x07,
            0xA0, 0x00, 0x00, 0x00, 0x04, 0x10, 0x10
        };

        std::cout << "Надсилання APDU кадру через C++ RAII верифікатор...\n";
        auto result = reader.sendApdu(select_aid);

        if (result) {
            std::cout << "Відповідь: " << result->payload.size() << " байтів, "
                      << "RTT: " << result->rtt.count() << " мкс\n";

            if (result->rtt > kMaxAllowedRtt) {
                std::cout << "[УВАГА! АТАКА] Затримка перевищує поріг! "
                          << "Виявлено ретранслятор.\n";
            } else {
                std::cout << "[OK] Автентичний тег у Ближній Зоні.\n";
            }
        } else {
            std::cerr << "Помилка обміну кадрами NFC.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток NFC: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
