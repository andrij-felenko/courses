/* ============================================================================
 * PowerManager.hpp — Ідіоматичний диспетчер живлення на C++20
 * ============================================================================ */
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <string_view>

namespace emb::pm {

enum class Mode : uint8_t {
    Active = 0,
    Sleep,
    Stop,
    Standby
};

enum class Lock : uint8_t {
    NoSleep = 0,
    NoStop,
    NoStandby,
    Count
};

/* Інтерфейс драйвера периферії, керованого за живленням */
class IPowerClient {
public:
    virtual ~IPowerClient() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual bool preSleep(Mode targetMode) noexcept = 0;
    virtual void postWakeup(Mode fromMode) noexcept = 0;
};

/* RAII Guard для автоматичного захоплення та звільнення блокування сну */
class [[nodiscard]] ScopedPowerLock {
public:
    explicit ScopedPowerLock(Lock lock) noexcept : m_lock(lock) {
        acquire(m_lock);
    }

    ~ScopedPowerLock() noexcept {
        if (m_active) {
            release(m_lock);
        }
    }

    ScopedPowerLock(const ScopedPowerLock&) = delete;
    ScopedPowerLock& operator=(const ScopedPowerLock&) = delete;

    ScopedPowerLock(ScopedPowerLock&& other) noexcept 
        : m_lock(other.m_lock), m_active(other.m_active) {
        other.m_active = false;
    }

    ScopedPowerLock& operator=(ScopedPowerLock&& other) noexcept {
        if (this != &other) {
            if (m_active) release(m_lock);
            m_lock = other.m_lock;
            m_active = other.m_active;
            other.m_active = false;
        }
        return *this;
    }

private:
    static void acquire(Lock lock) noexcept;
    static void release(Lock lock) noexcept;

    Lock m_lock;
    bool m_active{true};
};

/* Основний клас диспетчера енергозбереження */
class PowerManager {
public:
    static constexpr size_t MaxClients = 16;

    PowerManager() noexcept = default;

    static PowerManager& instance() noexcept {
        static PowerManager s_instance;
        return s_instance;
    }

    bool registerClient(IPowerClient* client) noexcept {
        if (!client || m_clientCount >= MaxClients) {
            return false;
        }
        m_clients[m_clientCount++] = client;
        return true;
    }

    void acquireLock(Lock lock) noexcept {
        auto idx = static_cast<size_t>(lock);
        if (idx < static_cast<size_t>(Lock::Count)) {
            m_lockCounters[idx].fetch_add(1, std::memory_order_relaxed);
        }
    }

    void releaseLock(Lock lock) noexcept {
        auto idx = static_cast<size_t>(lock);
        if (idx < static_cast<size_t>(Lock::Count)) {
            auto current = m_lockCounters[idx].load(std::memory_order_relaxed);
            while (current > 0 && !m_lockCounters[idx].compare_exchange_weak(
                current, current - 1, std::memory_order_relaxed)) {}
        }
    }

    [[nodiscard]] Mode deepestAllowedMode() const noexcept {
        if (m_lockCounters[static_cast<size_t>(Lock::NoSleep)].load(std::memory_order_relaxed) > 0) {
            return Mode::Active;
        }
        if (m_lockCounters[static_cast<size_t>(Lock::NoStop)].load(std::memory_order_relaxed) > 0) {
            return Mode::Sleep;
        }
        if (m_lockCounters[static_cast<size_t>(Lock::NoStandby)].load(std::memory_order_relaxed) > 0) {
            return Mode::Stop;
        }
        return Mode::Standby;
    }

    void sleepIfIdle(uint32_t expectedIdleMs) noexcept;

private:
    std::array<std::atomic<uint32_t>, static_cast<size_t>(Lock::Count)> m_lockCounters{};
    std::array<IPowerClient*, MaxClients> m_clients{};
    size_t m_clientCount{0};

    bool prepareClients(Mode targetMode) noexcept;
    void restoreClients(Mode fromMode) noexcept;
    void executeHardwareSleep(Mode mode, uint32_t idleMs) noexcept;
    void restoreClockTree() noexcept;
};

inline void ScopedPowerLock::acquire(Lock lock) noexcept {
    PowerManager::instance().acquireLock(lock);
}

inline void ScopedPowerLock::release(Lock lock) noexcept {
    PowerManager::instance().releaseLock(lock);
}

} // namespace emb::pm
