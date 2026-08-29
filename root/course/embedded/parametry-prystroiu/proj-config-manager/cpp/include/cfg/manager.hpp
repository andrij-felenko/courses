#pragma once
// manager.hpp — автомат конфігурації: холодний старт, міграція схеми,
// випробувальний режим із таймаутом, відкат і атомарний запис у Flash.

#include "cfg/config.hpp"
#include "cfg/flash.hpp"

#include <atomic>
#include <expected>
#include <mutex>

namespace cfg {

class Manager {
public:
    explicit Manager(Flash& flash) noexcept : flash_{flash}
    {
        live_.store(&active_config_, std::memory_order_relaxed);
    }

    Manager(const Manager&) = delete;
    Manager& operator=(const Manager&) = delete;

    // Читає обидва сектори, за потреби мігрує схему й піднімає робочий профіль.
    std::expected<void, Error> initialize();

    std::expected<void, Error> start_trial(const PayloadV2& candidate,
                                           std::uint32_t timeout_s = kTrialTimeoutS);
    std::expected<void, Error> confirm_commit();
    void rollback() noexcept;
    void tick_1hz() noexcept;   // тік із задачі системних таймерів

    // Робочий профіль для мережевого стека: під час випробування це кандидат.
    // Читання без блокувань — вказівник міняється атомарно; посилання дійсне
    // до наступної фіксації або відкату.
    [[nodiscard]] const PayloadV2& live() const noexcept
    {
        return *live_.load(std::memory_order_acquire);
    }

    [[nodiscard]] bool trial_active() const noexcept
    {
        return trial_running_.load(std::memory_order_relaxed);
    }
    [[nodiscard]] std::uint32_t seconds_left() const noexcept;
    [[nodiscard]] std::uint32_t sequence() const noexcept { return last_seq_; }
    [[nodiscard]] std::size_t active_slot() const noexcept { return active_slot_; }

    static std::expected<void, Error> validate(const PayloadV2& cfg) noexcept;
    static PayloadV2 factory_defaults() noexcept;
    static PayloadV2 migrate_v1_to_v2(const PayloadV1& v1);

private:
    [[nodiscard]] std::expected<Header, Error> valid_header(std::size_t slot) const noexcept;
    [[nodiscard]] std::expected<PayloadV2, Error> decode(std::size_t slot, const Header& hdr) const;
    std::expected<void, Error> write_record(const PayloadV2& cfg, std::uint32_t seq) noexcept;
    void rollback_locked() noexcept;

    Flash& flash_;
    mutable std::mutex mtx_;   // команди з мережі й тік таймера міняють один автомат

    // Стабільний профіль і випробувальний буфер — два окремі об'єкти:
    // відкат не відновлює дані, а лише повертає вказівник на стабільний.
    PayloadV2 active_config_{};
    PayloadV2 candidate_config_{};
    std::atomic<const PayloadV2*> live_{nullptr};

    std::atomic<bool> trial_running_{false};
    std::uint32_t trial_left_s_{0};
    std::uint32_t last_seq_{0};
    std::size_t active_slot_{0};   // 0 — Slot A, 1 — Slot B
};

}  // namespace cfg
