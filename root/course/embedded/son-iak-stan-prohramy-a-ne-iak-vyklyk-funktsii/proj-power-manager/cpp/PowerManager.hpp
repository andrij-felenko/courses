// PowerManager.hpp — диспетчер енергозбереження на C++23.
#pragma once

#include <array>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace emb::pm {

enum class Mode : std::uint8_t {
    Active = 0, // ядро та периферія активні
    Sleep,      // зупинено лише ядро, PLL живий
    Stop,       // PLL зупинено, SRAM збережено
    Standby     // домен ядра знеструмлено, пробудження = рестарт
};

enum class Lock : std::uint8_t {
    NoSleep = 0, // заборонено навіть зупиняти ядро
    NoStop,      // потрібні PLL і тактування шин APB
    NoStandby,   // потрібен уміст SRAM
    Count
};

[[nodiscard]] constexpr bool atLeastAsDeep(Mode a, Mode b) noexcept
{
    return static_cast<std::uint8_t>(a) >= static_cast<std::uint8_t>(b);
}

// Драйвер периферії, який має що сказати про сон.
class IPowerClient {
public:
    virtual ~IPowerClient() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    // false скасовує вхід у сон цілком; уже підготовлені драйвери відкочуються.
    [[nodiscard]] virtual bool preSleep(Mode targetMode) noexcept = 0;
    virtual void postWakeup(Mode fromMode) noexcept = 0;
};

class PowerManager {
public:
    static constexpr std::size_t MaxClients = 8;
    // Нижче цього горизонту перезапуск HSE+PLL з'їдає більше, ніж дає сон.
    static constexpr std::chrono::milliseconds Breakeven{3};

    [[nodiscard]] static PowerManager& instance() noexcept
    {
        static PowerManager s_instance;
        return s_instance;
    }

    void init() noexcept;

    bool registerClient(IPowerClient* client) noexcept;

    void acquireLock(Lock lock) noexcept;
    void releaseLock(Lock lock) noexcept;
    [[nodiscard]] std::uint32_t lockCount(Lock lock) const noexcept;
    // Зайвий release небезпечніший за витік: він знімає чужу заборону.
    [[nodiscard]] std::uint32_t lockUnderflows() const noexcept { return m_underflows; }

    [[nodiscard]] Mode deepestAllowedMode() const noexcept;

    // Головний вхід із циклу простою: expectedIdle — горизонт до найближчої події.
    void sleepIfIdle(std::chrono::milliseconds expectedIdle) noexcept;

    // STANDBY призначає застосунок, а не диспетчер: пробудження = рестарт.
    // Повертає false, якщо драйвер відмовив; інакше не повертається взагалі.
    [[nodiscard]] bool enterStandby(std::chrono::milliseconds wakeupAfter) noexcept;

    [[nodiscard]] std::uint32_t earlyWakeups() const noexcept { return m_earlyWakeups; }

private:
    PowerManager() noexcept = default;

    [[nodiscard]] std::span<IPowerClient* const> clients() const noexcept
    {
        return {m_clients.data(), m_clientCount};
    }

    [[nodiscard]] bool prepareClients(Mode targetMode) noexcept;
    void restoreClients(Mode fromMode) noexcept;
    static void enterLowPower(Mode mode) noexcept;

    std::array<std::atomic<std::uint32_t>, static_cast<std::size_t>(Lock::Count)> m_lockCounters{};
    std::array<IPowerClient*, MaxClients> m_clients{};
    std::size_t   m_clientCount{0};
    std::uint32_t m_underflows{0};
    std::uint32_t m_earlyWakeups{0};
};

// Блокування як ресурс: витік лічильника, що тримає плату в активному режимі
// роками, тут неможливий — деструктор відпрацює на будь-якому виході.
class [[nodiscard]] ScopedPowerLock {
public:
    explicit ScopedPowerLock(Lock lock) noexcept : m_lock{lock}
    {
        PowerManager::instance().acquireLock(m_lock);
    }

    ~ScopedPowerLock()
    {
        if (m_active) {
            PowerManager::instance().releaseLock(m_lock);
        }
    }

    ScopedPowerLock(const ScopedPowerLock&) = delete;
    ScopedPowerLock& operator=(const ScopedPowerLock&) = delete;

    ScopedPowerLock(ScopedPowerLock&& other) noexcept
        : m_lock{other.m_lock}, m_active{other.m_active}
    {
        other.m_active = false;
    }

    ScopedPowerLock& operator=(ScopedPowerLock&& other) noexcept
    {
        if (this != &other) {
            if (m_active) {
                PowerManager::instance().releaseLock(m_lock);
            }
            m_lock = other.m_lock;
            m_active = other.m_active;
            other.m_active = false;
        }
        return *this;
    }

    // Довга асинхронна транзакція переживає область видимості: блокування
    // віддається драйверові, який зніме його в обробнику завершення.
    void release() noexcept
    {
        if (m_active) {
            m_active = false;
            PowerManager::instance().releaseLock(m_lock);
        }
    }

private:
    Lock m_lock;
    bool m_active{true};
};

} // namespace emb::pm
