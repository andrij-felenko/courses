# ⚙️ Диспетчер енергозбереження: автомат режимів сну та блокування живлення

У складній вбудованій системі з десятками асинхронних драйверів (радіомодем, АЦП, Flash-пам'ять, давачі на шині I2C) жоден окремий модуль не володіє повною картиною стану мікроконтролера. Якщо драйвер радіопередавача вирішить викликати функцію переходу в глибокий сон, поки контролер прямого доступу до пам'яті (DMA) передає телеметричний лог у зовнішню пам'ять, тактування системної шини буде аварійно обірвано, а дані в мікросхемі Flash спотворено.

Для усунення цієї проблеми керування живленням виноситься в централізовану підсистему — диспетчер живлення (Power Manager). Його завдання полягає у координації життєвого циклу енергоспоживання між усіма програмними та апаратними компонентами пристрою:
1. Вести централізований облік вимог до живлення від усіх периферійних модулів через механізм блокувань енергозбереження (Power Locks / Quality of Service).
2. Визначати найглибший безпечний режим сну в моменти бездіяльності головного циклу на основі часового горизонту наступної запланованої події.
3. Координувати процедуру підготовки периферії (скидання черг, ізоляцію виводів GPIO) перед вимкненням тактових генераторів та відновлення робочої конфігурації після апаратного пробудження ядра.

Нижче наведено модульну, детерміновану та випробувану архітектуру диспетчера живлення для мікроконтролерів архітектури ARM Cortex-M на мовах C та C++.

## Архітектура та принцип роботи диспетчера

Диспетчер живлення побудований навколо трьох ключових концепцій:

1. **Градація режимів (Power Modes):**
   - `ACTIVE` — стандартне виконання коду, усі тактові генератори (HSE, PLL) та шинні мости (AHB, APB) ввімкнені.
   - `SLEEP` — зупинено тактування процесорного ядра (інструкція `WFI`), вся периферія, тактові генератори та оперативна пам'ять (SRAM) залишаються активними.
   - `STOP` (DeepSleep) — високовольтні генератори вимкнені, системний регулятор напруги переведений у режим низького споживання (Low-Power Regulator), збережено повний вміст SRAM, периферія знеструмлена.
   - `STANDBY` — живлення процесорного домену знято, оперативна пам'ять втрачається (за винятком кількох регістрів збереження), активний лише годинник реального часу (RTC) або контакт зовнішнього переривання. Пробудження еквівалентне перезапуску системи.

2. **Блокування сну (Power Locks):**
   Будь-який драйвер під час активної транзакції бере блокування відповідного рівня. Наприклад, передача пакета через UART вимагає активності шини APB і системного тактування, тому драйвер бере блокування `PM_LOCK_NO_STOP`. Поки лічильник цього блокування більший за нуль, диспетчер у головному циклі не має права переходити глибше режиму `SLEEP`.

3. **Хуки драйверів (Lifecycle Callbacks):**
   Перед переходом у режим `STOP` диспетчер викликає функцію `pre_sleep()` кожного зареєстрованого драйвера. Драйвер переводить свої виводи GPIO в аналоговий високоімпедансний стан, скидає буфери і вимикає тактування свого блоку. Після пробудження викликається `post_wakeup()`, де відновлюються конфігурація виводів та апаратні регістри.

## Інтерфейс диспетчера та облік блокувань

У мові C інтерфейс диспетчера надає процедурний API з лічильниками блокувань і масивом покажчиків на структури зворотних викликів. У C++ інтерфейс будується на абстрактному класі `IPowerClient` та обгортці керування ресурсами `ScopedPowerLock`, що гарантує детерміноване звільнення блокування при виході з області видимості за патерном RAII (Resource Acquisition Is Initialization).

:::tabs
```c
/* ============================================================================
 * power_manager.h — Диспетчер енергозбереження на мові C
 * ============================================================================ */
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Рівні енергозбереження мікроконтролера */
typedef enum {
    PM_MODE_ACTIVE = 0, /* Ядро та периферія активні */
    PM_MODE_SLEEP,      /* Ядро зупинено, периферія та PLL активні */
    PM_MODE_STOP,       /* PLL зупинено, SRAM збережено, мікроспоживання */
    PM_MODE_STANDBY     /* Повне знеструмлення ядра, рестарт по RTC */
} pm_mode_t;

/* Типи блокувань енергозбереження */
typedef enum {
    PM_LOCK_NO_SLEEP   = 0, /* Заборона навіть легкого сну (WFI) */
    PM_LOCK_NO_STOP    = 1, /* Заборона переходу в STOP (потрібні PLL або APB) */
    PM_LOCK_NO_STANDBY = 2, /* Заборона переходу в STANDBY (потрібна пам'ять SRAM) */
    PM_LOCK_COUNT
} pm_lock_t;

/* Структура хуків життєвого циклу периферійного драйвера */
typedef struct {
    const char *name;
    /* Викликається перед зупинкою тактування. Якщо повертає false — вхід скасовується */
    bool (*pre_sleep)(pm_mode_t target_mode);
    /* Викликається після відновлення PLL та системної частоти */
    void (*post_wakeup)(pm_mode_t from_mode);
} pm_driver_client_t;

/* Ініціалізація диспетчера живлення */
void pm_init(void);

/* Реєстрація клієнта (драйвера периферії) */
bool pm_register_client(const pm_driver_client_t *client);

/* Захоплення блокування (збільшує лічильник відповідного блокування) */
void pm_lock_acquire(pm_lock_t lock);

/* Звільнення блокування (зменшує лічильник) */
void pm_lock_release(pm_lock_t lock);

/* Опитування найглибшого дозволеного режиму сну */
pm_mode_t pm_get_deepest_allowed_mode(void);

/* Головна функція диспетчера: оцінює блокування та атомарно занурює систему в сон */
void pm_sleep_if_idle(uint32_t expected_idle_ms);

#ifdef __cplusplus
}
#endif

#endif /* POWER_MANAGER_H */
```
```cpp
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
```
:::

## Реалізація логіки переходу та апаратного узгодження

Головна складність реалізації диспетчера полягає в гарантуванні атомарності переходу та збереженні цілісності тактових генераторів. Коли мікроконтролер прокидається з режиму `STOP`, його апаратна частина автоматично перемикається на низькошвидкісний внутрішній RC-генератор (наприклад, HSI16 або MSI на частоті 4 МГц). Якщо код одразу почне звертатися до периферії або пам'яті, розрахованої на роботу від зовнішнього кварцу 80 МГц, станеться збій інтерфейсів або спотворення швидкостей обміну.

З цієї причини диспетчер відновлює дерево тактування (контур PLL та системні дільники шин) **до** того, як дозволяє виконання накопичених обробників переривань.

:::tabs
```c
/* ============================================================================
 * power_manager.c — Реалізація диспетчера та апаратної взаємодії
 * ============================================================================ */
#include "power_manager.h"
#include <string.h>

/* Псевдо-регістри та інтринсики Cortex-M для автономності прикладу */
#ifndef __NOP
#define __NOP()                 __asm volatile ("nop")
#define __WFI()                 __asm volatile ("wfi")
#define __DSB()                 __asm volatile ("dsb 0xF" ::: "memory")
#define __ISB()                 __asm volatile ("isb 0xF" ::: "memory")
#define __disable_irq()         __asm volatile ("cpsid i" : : : "memory")
#define __enable_irq()          __asm volatile ("cpsie i" : : : "memory")
#endif

#define MAX_PM_CLIENTS 16

static uint32_t s_locks[PM_LOCK_COUNT];
static const pm_driver_client_t *s_clients[MAX_PM_CLIENTS];
static size_t s_client_count = 0;

void pm_init(void) {
    memset(s_locks, 0, sizeof(s_locks));
    memset(s_clients, 0, sizeof(s_clients));
    s_client_count = 0;
}

bool pm_register_client(const pm_driver_client_t *client) {
    if (!client || s_client_count >= MAX_PM_CLIENTS) {
        return false;
    }
    s_clients[s_client_count++] = client;
    return true;
}

void pm_lock_acquire(pm_lock_t lock) {
    if (lock < PM_LOCK_COUNT) {
        __disable_irq();
        s_locks[lock]++;
        __enable_irq();
    }
}

void pm_lock_release(pm_lock_t lock) {
    if (lock < PM_LOCK_COUNT) {
        __disable_irq();
        if (s_locks[lock] > 0) {
            s_locks[lock]--;
        }
        __enable_irq();
    }
}

pm_mode_t pm_get_deepest_allowed_mode(void) {
    if (s_locks[PM_LOCK_NO_SLEEP] > 0)   return PM_MODE_ACTIVE;
    if (s_locks[PM_LOCK_NO_STOP] > 0)    return PM_MODE_SLEEP;
    if (s_locks[PM_LOCK_NO_STANDBY] > 0) return PM_MODE_STOP;
    return PM_MODE_STANDBY;
}

/* Відновлення високошвидкісного дерева тактування після пробудження з режиму STOP */
static void pm_restore_clock_tree(void) {
    /* 1. Запуск зовнішнього високочастотного кварцового генератора (HSE) */
    /* RCC->CR |= RCC_CR_HSEON; while (!(RCC->CR & RCC_CR_HSERDY)); */

    /* 2. Запуск помножувача частоти PLL */
    /* RCC->CR |= RCC_CR_PLLON; while (!(RCC->CR & RCC_CR_PLLRDY)); */

    /* 3. Перемикання системної шини SYSCLK на вихід PLL */
    /* RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL; */
}

/* Налаштування апаратного таймера низького споживання (LPTIM / RTC Wakeup) */
static void pm_setup_wakeup_timer(uint32_t ms) {
    /* Програмування регістрів авто-пробудження RTC Wakeup або LPTIM */
    (void)ms;
}

void pm_sleep_if_idle(uint32_t expected_idle_ms) {
    pm_mode_t target_mode = pm_get_deepest_allowed_mode();

    if (target_mode == PM_MODE_ACTIVE) {
        /* Сон повністю заблокований, повертаємося до виконання задач */
        return;
    }

    if (target_mode == PM_MODE_SLEEP) {
        /* Легкий сон: вимикаємо лише ядро, переривання миттєво піднімуть систему */
        __WFI();
        return;
    }

    /* Глибокий сон: вимагає узгодження з усіма периферійними клієнтами */
    size_t prepared_clients = 0;
    for (size_t i = 0; i < s_client_count; ++i) {
        if (s_clients[i]->pre_sleep) {
            if (!s_clients[i]->pre_sleep(target_mode)) {
                /* Клієнт відхилив вхід у сон — відкочуємо вже підготовлені модулі */
                for (size_t j = 0; j < prepared_clients; ++j) {
                    if (s_clients[j]->post_wakeup) {
                        s_clients[j]->post_wakeup(target_mode);
                    }
                }
                return;
            }
        }
        prepared_clients++;
    }

    /* Налаштовуємо джерело пробудження за часом */
    pm_setup_wakeup_timer(expected_idle_ms);

    /* АТОМАРНИЙ ВХІД: блокуємо виконання ISR, щоб уникнути гонитви переривань */
    __disable_irq();

    /* Перевіряємо, чи не з'явилися нові блокування за час підготовки клієнтів */
    if (pm_get_deepest_allowed_mode() >= target_mode) {
        /* Налаштування регістра керування системою Cortex-M System Control Register */
        /* SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk; */

        __DSB();
        __ISB();

        /* Перехід у глибокий сон: ядро засинає, але будь-яке виставлене переривання розбудить його */
        __WFI();

        /* Скидання біта глибокого сну після пробудження */
        /* SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk; */
    }

    /* 1. Відновлюємо тактування (HSE/PLL) ДО виклику обробників ISR */
    pm_restore_clock_tree();

    /* 2. Дозволяємо процесору виконати накопичені апаратні переривання */
    __enable_irq();

    /* 3. Сповіщаємо всі драйвери про повернення в активний режим */
    for (size_t i = 0; i < s_client_count; ++i) {
        if (s_clients[i]->post_wakeup) {
            s_clients[i]->post_wakeup(target_mode);
        }
    }
}
```
```cpp
/* ============================================================================
 * PowerManager.cpp — Реалізація диспетчера на C++20
 * ============================================================================ */
#include "PowerManager.hpp"

namespace emb::pm {

namespace {

inline void disableInterrupts() noexcept {
    __asm volatile ("cpsid i" : : : "memory");
}

inline void enableInterrupts() noexcept {
    __asm volatile ("cpsie i" : : : "memory");
}

inline void dataSyncBarrier() noexcept {
    __asm volatile ("dsb 0xF" ::: "memory");
}

inline void instrSyncBarrier() noexcept {
    __asm volatile ("isb 0xF" ::: "memory");
}

inline void waitForInterrupt() noexcept {
    __asm volatile ("wfi");
}

} // anonymous namespace

bool PowerManager::prepareClients(Mode targetMode) noexcept {
    size_t prepared = 0;
    for (size_t i = 0; i < m_clientCount; ++i) {
        if (m_clients[i] && !m_clients[i]->preSleep(targetMode)) {
            // Відкат у зворотному порядку для вже підготовлених драйверів
            for (size_t j = prepared; j > 0; --j) {
                m_clients[j - 1]->postWakeup(targetMode);
            }
            return false;
        }
        ++prepared;
    }
    return true;
}

void PowerManager::restoreClients(Mode fromMode) noexcept {
    for (size_t i = 0; i < m_clientCount; ++i) {
        if (m_clients[i]) {
            m_clients[i]->postWakeup(fromMode);
        }
    }
}

void PowerManager::restoreClockTree() noexcept {
    // 1. Увімкнення зовнішнього кварцового генератора (HSE)
    // 2. Очікування прапорця стабілізації HSERDY
    // 3. Запуск контуру фазового автопідстроювання PLL
    // 4. Перемикання системної шини на PLL
}

void PowerManager::executeHardwareSleep(Mode mode, uint32_t idleMs) noexcept {
    (void)idleMs;

    disableInterrupts();

    // Повторна атомарна перевірка блокувань
    if (deepestAllowedMode() >= mode) {
        if (mode == Mode::Stop) {
            // Встановлення біта SLEEPDEEP у системному регістрі Cortex-M SCB->SCR
            dataSyncBarrier();
            instrSyncBarrier();
        }

        waitForInterrupt();

        if (mode == Mode::Stop) {
            // Скидання біта SLEEPDEEP
        }
    }

    if (mode == Mode::Stop) {
        restoreClockTree();
    }

    enableInterrupts();
}

void PowerManager::sleepIfIdle(uint32_t expectedIdleMs) noexcept {
    const Mode target = deepestAllowedMode();

    if (target == Mode::Active) {
        return;
    }

    if (target == Mode::Sleep) {
        waitForInterrupt();
        return;
    }

    if (!prepareClients(target)) {
        return;
    }

    executeHardwareSleep(target, expectedIdleMs);

    restoreClients(target);
}

} // namespace emb::pm
```
:::

## Інтеграція в драйвери периферії: керування життєвим циклом

Розглянемо практичний приклад: драйвер зовнішньої Flash-пам'яті по шині SPI. Під час сесії запису секторів Flash-пам'ять не повинна бути знеструмлена, а тактування SPI має залишатися стабільним. Коли запис завершено, драйвер переводить мікросхему Flash у режим ультранизького споживання (Deep Power-Down, команда `0xB9`), а виводи SPI CS, SCK, MOSI ізолює, переводячи в аналоговий стан.

:::tabs
```c
/* ============================================================================
 * spi_flash_driver.c — Драйвер Flash з інтеграцією в диспетчер живлення (C)
 * ============================================================================ */
#include "power_manager.h"
#include <stdbool.h>

static bool s_flash_busy = false;

static bool flash_pre_sleep_hook(pm_mode_t target_mode) {
    if (s_flash_busy) {
        /* Забороняємо глибокий сон під час запису секторів */
        return false;
    }

    if (target_mode == PM_MODE_STOP || target_mode == PM_MODE_STANDBY) {
        /* 1. Відправка апаратної команди Deep Power Down (0xB9) у мікросхему */
        /* spi_send_byte(0xB9); */

        /* 2. Переведення ліній шини SPI (SCK, MOSI, MISO) у режим Analog High-Z */
        /* gpio_set_mode_analog(SPI_PINS); */
    }
    return true;
}

static void flash_post_wakeup_hook(pm_mode_t from_mode) {
    if (from_mode == PM_MODE_STOP || from_mode == PM_MODE_STANDBY) {
        /* 1. Відновлення режимів альтернативної функції для пінів SPI */
        /* gpio_set_mode_af(SPI_PINS); */

        /* 2. Пробудження мікросхеми Flash сигналом Chip Select або командою 0xAB */
        /* spi_send_byte(0xAB); */
    }
}

static const pm_driver_client_t s_flash_client = {
    .name = "SPI_Flash",
    .pre_sleep = flash_pre_sleep_hook,
    .post_wakeup = flash_post_wakeup_hook
};

void spi_flash_init(void) {
    pm_register_client(&s_flash_client);
}

void spi_flash_write_sector_async(uint32_t address, const uint8_t *data, size_t len) {
    (void)address; (void)data; (void)len;

    /* Захоплюємо блокування: забороняємо системі переходити в режим STOP під час DMA */
    pm_lock_acquire(PM_LOCK_NO_STOP);
    s_flash_busy = true;

    /* Запуск асинхронної передачі через DMA... */
}

/* Обробник переривання завершення DMA передачі */
void DMA1_Channel3_IRQHandler(void) {
    /* Очищення прапорця завершення передачі */
    s_flash_busy = false;

    /* Звільняємо блокування — система знову має право заснути в глибокий режим STOP */
    pm_lock_release(PM_LOCK_NO_STOP);
}
```
```cpp
/* ============================================================================
 * SpiFlashDriver.hpp — Драйвер Flash з використанням RAII ScopedPowerLock (C++)
 * ============================================================================ */
#pragma once

#include "PowerManager.hpp"
#include <span>

namespace emb::drivers {

class SpiFlashDriver final : public pm::IPowerClient {
public:
    SpiFlashDriver() noexcept {
        pm::PowerManager::instance().registerClient(this);
    }

    [[nodiscard]] std::string_view name() const noexcept override {
        return "SpiFlash";
    }

    [[nodiscard]] bool preSleep(pm::Mode targetMode) noexcept override {
        if (m_busy.load(std::memory_order_acquire)) {
            return false;
        }

        if (targetMode == pm::Mode::Stop || targetMode == pm::Mode::Standby) {
            // Переведення зовнішньої Flash у Deep Power Down (0xB9)
            // Ізоляція виводів SPI в стан Analog High-Z
        }
        return true;
    }

    void postWakeup(pm::Mode fromMode) noexcept override {
        if (fromMode == pm::Mode::Stop || fromMode == pm::Mode::Standby) {
            // Відновлення пінів SPI та пробудження Flash (0xAB)
        }
    }

    // Синхронний запис із гарантією збереження живлення через RAII блокування
    bool writeBuffer(uint32_t address, std::span<const uint8_t> data) noexcept {
        (void)address; (void)data;

        // Автоматично захоплює блокування NoStop при вході в область видимості
        // та звільняє його при будь-якому виході (навіть при помилці)
        pm::ScopedPowerLock lockGuard(pm::Lock::NoStop);

        m_busy.store(true, std::memory_order_release);

        // Виконання передачі по шині SPI...

        m_busy.store(false, std::memory_order_release);
        return true;
    }

private:
    std::atomic<bool> m_busy{false};
};

} // namespace emb::drivers
```
:::

## Інтеграція з бестіковим планувальником (Tickless Idle)

У традиційних операційних системах реального часу (FreeRTOS, Zephyr) щомілісекунди генерується системне переривання SysTick для перемикання квантів часу. Це переривання примусово будить процесор 1000 разів на секунду, навіть якщо всі задачі очікують подій і в системі немає корисної роботи. За 1 мс ядро встигає лише прокинутися, перевірити таймери й знову заснути, витрачаючи енергію на перезапуск PLL.

Режим Tickless Idle повністю вимикає системний таймер SysTick на час бездіяльності і перераховує часовий інтервал до найближчого дедлайну задачі:

```text
Δt_idle = min(T_next_timer_1, T_next_timer_2, ..., T_task_timeout) - T_current
```

Цей інтервал передається у функцію `pm_sleep_if_idle(Δt_idle)`. Якщо `Δt_idle` перевищує точку беззбитковості (breakeven time, зазвичай 2–5 мс), диспетчер програмує апаратний низькоспоживаючий таймер LPTIM або RTC Wakeup і занурює процесор у режим `STOP`. При пробудженні диспетчер зчитує лічильник реального часу, компенсує системний лічильник тіків ОС і поновлює роботу планувальника задач без накопичення похибки часу.

## Типові помилки та архітектурні пастки

1. **Витік блокувань (Leaked Power Locks):**
   Якщо драйвер захопив блокування `pm_lock_acquire()`, але в результаті помилки передачі (наприклад, таймауту відповіді датчика) вийшов із функції без виклику `pm_lock_release()`, лічильник блокувань назавжди залишиться додатним. Мікроконтролер більше ніколи не увійде в глибокий сон, розряджаючи батарею за кілька діб замість кількох років. У коді на C++ ця проблема надійно вирішується класом `ScopedPowerLock`, який використовує семантику RAII для детермінованого звільнення ресурсу в деструкторі.

2. **Блокуючі операції всередині хуків `pre_sleep()`:**
   Хук `pre_sleep()` повинен виконуватися швидко і без очікування зовнішніх подій. Якщо драйвер спробує всередині хука передати довгий буфер через блокуючий виклик UART зі швидкістю 9600 бод, це затримає вхід у сон на десятки мілісекунд і зламає часові бюджети енергоспоживання. Усі дані повинні бути скинуті заздалегідь під захистом блокування `PM_LOCK_NO_STOP`, а хук `pre_sleep()` має виконувати виключно прямі операції з регістрами керування GPIO та живлення.

3. **Неправильний порядок відновлення тактування:**
   Звернення до периферії або виконання обчислень до того, як стабілізується зовнішній кварц (HSE) та зафіксується контур PLL, призводить до спотворення швидкостей інтерфейсів (бодрейту UART, частоти SPI) або апаратного зависання процесора на несумісних дільниках шини. Диспетчер живлення завжди повинен спочатку гарантувати фіксацію частоти шин, і лише потім передавати керування обробникам переривань та клієнтським хукам.
