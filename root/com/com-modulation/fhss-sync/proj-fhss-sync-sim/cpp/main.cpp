#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <optional>
#include <format>

enum class SyncState {
    Searching,
    Locking,
    Tracking,
    LostSync
};

class FhssTransmitter {
public:
    explicit FhssTransmitter(uint16_t seed, uint8_t channel_count = 8)
        : m_lfsr_state(seed), m_channel_count(channel_count), m_current_hop(0) {}

    uint8_t step() {
        m_current_hop++;
        uint16_t bit = ((m_lfsr_state >> 0) ^ (m_lfsr_state >> 2) ^ 
                        (m_lfsr_state >> 3) ^ (m_lfsr_state >> 5)) & 1;
        m_lfsr_state = (m_lfsr_state >> 1) | (bit << 7);
        return static_cast<uint8_t>(m_lfsr_state % m_channel_count);
    }

    [[nodiscard]] uint16_t state() const noexcept { return m_lfsr_state; }
    [[nodiscard]] uint32_t current_hop() const noexcept { return m_current_hop; }

private:
    uint16_t m_lfsr_state;
    uint8_t  m_channel_count;
    uint32_t m_current_hop;
};

class FhssReceiver {
public:
    struct Config {
        uint8_t  channel_count = 8;
        int32_t  guard_time_us = 150;
        uint8_t  max_missed_hops = 5;
        uint8_t  scan_channel = 3;
    };

    explicit FhssReceiver(Config config = {})
        : m_config(config), m_state(SyncState::Searching) {}

    void process_hop(uint8_t tx_channel, uint16_t tx_seed, uint32_t tx_hop, int32_t drift_us) {
        m_timer_offset_us += drift_us;

        switch (m_state) {
            case SyncState::Searching:
                std::cout << std::format("[SEARCH] Rx на каналі {}... Tx на {}\n", 
                                         m_config.scan_channel, tx_channel);
                if (tx_channel == m_config.scan_channel) {
                    m_state = SyncState::Locking;
                    m_lfsr_state = tx_seed;
                    m_current_hop = tx_hop;
                    m_timer_offset_us = 0;
                    m_missed_count = 0;
                    std::cout << std::format("  -> [EVENT] Преамбулу знайдено! Hop={}\n", tx_hop);
                }
                break;

            case SyncState::Locking:
                m_state = SyncState::Tracking;
                std::cout << "  -> [FSM] Перехід у TRACKING\n";
                break;

            case SyncState::Tracking: {
                m_current_hop++;
                uint8_t expected_ch = next_expected_channel();

                bool time_ok = (std::abs(m_timer_offset_us) <= m_config.guard_time_us);
                bool ch_ok = (expected_ch == tx_channel);

                if (time_ok && ch_ok) {
                    std::cout << std::format("[TRACKING] Hop {}: Канал {} OK (Дрейф: {} us)\n",
                                             m_current_hop, expected_ch, m_timer_offset_us);
                    /* Петльова корекція таймера (Early-Late) */
                    m_timer_offset_us /= 2;
                    m_missed_count = 0;
                } else {
                    m_missed_count++;
                    std::cout << std::format("[TRACKING] Hop {}: Пропуск! (Missed={}/{})\n",
                                             m_current_hop, m_missed_count, m_config.max_missed_hops);

                    if (m_missed_count >= m_config.max_missed_hops) {
                        m_state = SyncState::LostSync;
                    }
                }
                break;
            }

            case SyncState::LostSync:
                std::cout << "  -> [ALERT] Втрата синхронізму! Скидання\n";
                m_state = SyncState::Searching;
                m_missed_count = 0;
                break;
        }
    }

    [[nodiscard]] SyncState current_state() const noexcept { return m_state; }

private:
    uint8_t next_expected_channel() {
        uint16_t bit = ((m_lfsr_state >> 0) ^ (m_lfsr_state >> 2) ^ 
                        (m_lfsr_state >> 3) ^ (m_lfsr_state >> 5)) & 1;
        m_lfsr_state = (m_lfsr_state >> 1) | (bit << 7);
        return static_cast<uint8_t>(m_lfsr_state % m_config.channel_count);
    }

    Config     m_config;
    SyncState  m_state;
    uint16_t   m_lfsr_state{0};
    uint32_t   m_current_hop{0};
    int32_t    m_timer_offset_us{0};
    uint8_t    m_missed_count{0};
};

int main() {
    FhssTransmitter tx(0xACE1);
    FhssReceiver rx;

    std::cout << "=== C++20 FHSS SYNC SIMULATION ===\n\n";

    for (int step = 0; step < 20; ++step) {
        uint16_t seed_before = tx.state();
        uint8_t tx_ch = tx.step();
        rx.process_hop(tx_ch, seed_before, tx.current_hop(), 45);
    }

    return 0;
}
