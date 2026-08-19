# ⚙️ Програмна реалізація контролера шини I3C: автомат станів DAA та диспетчер IBI

Програмне керування шиною MIPI I3C вимагає підтримки гібридного протокольного рівня: керування динамічним перемиканням драйверів виводів між відкритим стоком (*Open-Drain*) та двотактним каскадом (*Push-Pull*), виконання побітового арбітражу 48-бітних тимчасових ідентифікаторів (*Provisional ID*) під час процедури `ENTDAA`, формування перехідних бітів парності (*T-bit*) та реєстрації асинхронних внутрішньосмугових переривань (*IBI*).

Нижче наведено модульну програмну архітектуру контролера шини I3C.

---

### Архітектура інтерфейсу та структури даних контролера

Контролер шини підтримує внутрішній реєстр дескрипторів усіх виявлених цільових пристроїв (*Targets*). Для кожного вузла зберігається його 48-бітний апаратний ідентифікатор `Provisional ID`, регістри можливостей `BCR` і `DCR`, а також призначена під час ініціалізації 7-бітна динамічна адреса.

Кожен пристрій на шині I3C проходить етап реєстрації у внутрішній таблиці дескрипторів контролера. Структура дескриптора фіксує не лише статичні параметри чипа, але й динамічний стан: чи дозволені наразі переривання IBI, чи підтримує пристрій передачу додаткових байтів корисного навантаження, та який максимальний ліміт довжини читання й запису призначено вузлу під час конфігурації.

:::tabs
```c
/* i3c_controller.h - Базовий C-інтерфейс та структури контролера I3C */
#ifndef I3C_CONTROLLER_H
#define I3C_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define I3C_BROADCAST_ADDR  0x7E
#define I3C_CCC_ENTDAA      0x07
#define I3C_CCC_ENEC        0x00
#define I3C_CCC_DISEC       0x01
#define I3C_MAX_DEVICES     16

typedef enum {
    I3C_STATUS_OK = 0,
    I3C_STATUS_NACK,
    I3C_STATUS_BUS_LOST,
    I3C_STATUS_PARITY_ERROR,
    I3C_STATUS_TIMEOUT,
    I3C_STATUS_NO_DEVICES
} i3c_status_t;

typedef struct {
    uint64_t provisional_id; /* 48-бітний апаратний ID */
    uint8_t  bcr;            /* Bus Characteristics Register */
    uint8_t  dcr;            /* Device Characteristics Register */
    uint8_t  dynamic_addr;   /* Призначена 7-бітна динамічна адреса */
    bool     ibi_enabled;    /* Дозвіл переривань IBI */
} i3c_target_desc_t;

typedef struct {
    i3c_target_desc_t targets[I3C_MAX_DEVICES];
    size_t target_count;
    uint8_t next_free_addr;
} i3c_bus_context_t;

/* Обчислення непарного T-біта парності (Odd Parity) */
static inline uint8_t i3c_calc_t_bit(uint8_t byte) {
    byte ^= byte >> 4;
    byte ^= byte >> 2;
    byte ^= byte >> 1;
    return (uint8_t)(~byte & 0x01);
}

/* Ініціалізація контексту шини */
void i3c_bus_init(i3c_bus_context_t *ctx);

/* Процедура динамічного призначення адрес (ENTDAA) */
i3c_status_t i3c_perform_daa(i3c_bus_context_t *ctx);

/* Запис блоку даних цільовому пристрою у режимі SDR */
i3c_status_t i3c_sdr_write(i3c_bus_context_t *ctx, uint8_t dyn_addr,
                           const uint8_t *data, size_t len);

/* Зчитування блоку даних від цільового пристрою у режимі SDR */
i3c_status_t i3c_sdr_read(i3c_bus_context_t *ctx, uint8_t dyn_addr,
                          uint8_t *buffer, size_t max_len, size_t *actual_len);

/* Обробник внутрішньосмугового переривання IBI */
i3c_status_t i3c_handle_ibi(i3c_bus_context_t *ctx, uint8_t *winning_addr,
                            uint8_t *mdb);

#endif /* I3C_CONTROLLER_H */
```
```cpp
// i3c_controller.hpp - Ідіоматичний C++20 інтерфейс з RAII та строгими типами
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <algorithm>

namespace mipi::i3c {

enum class Status : uint8_t {
    Ok = 0,
    Nack,
    ArbitrationLost,
    ParityError,
    Timeout,
    NoDevices,
    BufferOverflow
};

struct ProvisionalId {
    uint64_t value : 48;

    [[nodiscard]] constexpr uint16_t vendor_id() const noexcept {
        return static_cast<uint16_t>((value >> 33) & 0x7FFF);
    }
    [[nodiscard]] constexpr uint16_t part_id() const noexcept {
        return static_cast<uint16_t>((value >> 16) & 0xFFFF);
    }
    [[nodiscard]] constexpr uint8_t instance_id() const noexcept {
        return static_cast<uint8_t>((value >> 12) & 0x0F);
    }
};

struct TargetDescriptor {
    ProvisionalId id{};
    uint8_t bcr{0};
    uint8_t dcr{0};
    uint8_t dynamic_address{0};
    bool ibi_capable{false};
    bool ibi_has_payload{false};
};

class BusController {
public:
    static constexpr size_t MaxTargets = 16;
    static constexpr uint8_t BroadcastAddress = 0x7E;
    static constexpr uint8_t StartDynamicAddress = 0x08;

    constexpr BusController() noexcept : next_address_(StartDynamicAddress) {}

    [[nodiscard]] std::expected<size_t, Status> run_dynamic_address_assignment() noexcept {
        targets_count_ = 0;
        next_address_ = StartDynamicAddress;

        // Генерація широкомовної команди ENTDAA (0x07)
        if (auto res = send_broadcast_ccc(0x07); !res) {
            return std::unexpected(res.error());
        }

        while (targets_count_ < MaxTargets) {
            auto target_info = probe_target_provisional_id();
            if (!target_info.has_value()) {
                break; // Усі доступні пристрої отримали адреси
            }

            const uint8_t assigned_addr = next_address_++;
            if (!assign_address_to_winner(assigned_addr)) {
                return std::unexpected(Status::Nack);
            }

            TargetDescriptor desc{
                .id = target_info->id,
                .bcr = target_info->bcr,
                .dcr = target_info->dcr,
                .dynamic_address = assigned_addr,
                .ibi_capable = (target_info->bcr & 0x02) != 0,
                .ibi_has_payload = (target_info->bcr & 0x04) != 0
            };

            targets_[targets_count_++] = desc;
        }

        if (targets_count_ == 0) {
            return std::unexpected(Status::NoDevices);
        }
        return targets_count_;
    }

    [[nodiscard]] std::expected<void, Status> write_sdr(
        uint8_t address, std::span<const uint8_t> data) noexcept 
    {
        if (!start_transfer(address, false)) {
            return std::unexpected(Status::Nack);
        }

        for (uint8_t byte : data) {
            const uint8_t t_bit = calculate_parity_t_bit(byte);
            if (!push_pull_write_byte(byte, t_bit)) {
                send_stop();
                return std::unexpected(Status::ParityError);
            }
        }

        send_stop();
        return {};
    }

    [[nodiscard]] std::expected<size_t, Status> read_sdr(
        uint8_t address, std::span<uint8_t> buffer) noexcept 
    {
        if (!start_transfer(address, true)) {
            return std::unexpected(Status::Nack);
        }

        size_t bytes_read = 0;
        for (auto& slot : buffer) {
            auto [byte, is_last] = push_pull_read_byte();
            slot = byte;
            bytes_read++;
            if (is_last) {
                break;
            }
        }

        send_stop();
        return bytes_read;
    }

    [[nodiscard]] std::span<const TargetDescriptor> active_targets() const noexcept {
        return std::span<const TargetDescriptor>(targets_.data(), targets_count_);
    }

private:
    [[nodiscard]] static constexpr uint8_t calculate_parity_t_bit(uint8_t b) noexcept {
        b ^= b >> 4;
        b ^= b >> 2;
        b ^= b >> 1;
        return static_cast<uint8_t>(~b & 0x01);
    }

    std::expected<void, Status> send_broadcast_ccc(uint8_t ccc_code) noexcept;
    std::optional<TargetDescriptor> probe_target_provisional_id() noexcept;
    bool assign_address_to_winner(uint8_t dyn_addr) noexcept;
    bool start_transfer(uint8_t addr, bool is_read) noexcept;
    bool push_pull_write_byte(uint8_t data, uint8_t t_bit) noexcept;
    std::pair<uint8_t, bool> push_pull_read_byte() noexcept;
    void send_stop() noexcept;

    std::array<TargetDescriptor, MaxTargets> targets_{};
    size_t targets_count_{0};
    uint8_t next_address_{StartDynamicAddress};
};

} // namespace mipi::i3c
```
:::

---

### Детальний розбір реалізації автомата станів DAA та обробки IBI

Автомат станів ініціалізації шини керує послідовністю опитування невідомої топології пристроїв. Оскільки кількість давачів на платі заздалегідь не зафіксована у коді драйвера, цикл `ENTDAA` виконується динамічно до першої негативної відповіді шини.

Послідовність виконання процедури DAA:
1. **Широкомовний вхід у DAA:** Контролер генерує стартову умову і відправляє байт `0x7E << 1` (запис) на відкритому стоці. Отримавши підтвердження ACK від одного чи кількох ведених пристроїв, контролер передає код команди `0x07` (`ENTDAA`).
2. **Раунд побітового арбітражу:** Контролер формує повторний старт (*Repeated START*) та надсилає адресу `(0x7E << 1) | 0x01` (читання). Усі неініціалізовані чипи одночасно виставляють старший біт свого 48-бітного `Provisional ID`.
3. **Визначення переможця:** На кожному тактовому імпульсі SCL контролер зчитує стан лінії SDA. Оскільки нуль є домінантним станом, чипи, у яких поточний біт дорівнює `1`, бачать на шині нуль і миттєво відключають свої вихідні буфери до наступного раунду. До кінця 48-го біта на лінії залишається рівно один переможець.
4. **Читання регістрів дескриптора:** Переможець арбітражу передає 8 бітів регістра характеристик шини `BCR` та 8 бітів регістра типу пристрою `DCR`.
5. **Призначення адреси:** Контролер формує 7-бітну динамічну адресу (починаючи з `0x08`), упаковує її з бітом парності та відправляє переможцю. Ціль фіксує нову адресу у внутрішньому регістрі й вимикає свою участь у подальших раундах `ENTDAA`.
6. **Завершення сканування:** Контролер повторює кроки 2–5. Коли всі пристрої отримали адреси, на черговий запит читання `0x7E` лінія SDA залишається у високому стані (NACK). Контролер фіксує вичерпання неініціалізованих вузлів, формує стан STOP та переходить у робочий режим.

:::tabs
```c
/* i3c_controller.c - Реалізація логіки DAA та диспетчера IBI */
#include "i3c_controller.h"
#include <string.h>

void i3c_bus_init(i3c_bus_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(i3c_bus_context_t));
    ctx->next_free_addr = 0x08; /* Перші 8 адрес зарезервовані */
}

/* Імітація апаратних функцій нижнього рівня */
extern void hw_i3c_start_open_drain(void);
extern void hw_i3c_stop_open_drain(void);
extern bool hw_i3c_write_byte_od(uint8_t byte);
extern bool hw_i3c_read_pid_bcr_dcr(uint64_t *pid, uint8_t *bcr, uint8_t *dcr);
extern bool hw_i3c_assign_addr_od(uint8_t addr);

i3c_status_t i3c_perform_daa(i3c_bus_context_t *ctx) {
    if (!ctx) return I3C_STATUS_BUS_LOST;

    ctx->target_count = 0;
    ctx->next_free_addr = 0x08;

    /* 1. START та широкомовна адреса 0x7E (W) */
    hw_i3c_start_open_drain();
    if (!hw_i3c_write_byte_od(I3C_BROADCAST_ADDR << 1)) {
        hw_i3c_stop_open_drain();
        return I3C_STATUS_NACK;
    }

    /* 2. Командний код CCC 0x07 (ENTDAA) */
    if (!hw_i3c_write_byte_od(I3C_CCC_ENTDAA)) {
        hw_i3c_stop_open_drain();
        return I3C_STATUS_NACK;
    }

    /* 3. Цикл арбітражу та роздачі адрес */
    while (ctx->target_count < I3C_MAX_DEVICES) {
        uint64_t pid = 0;
        uint8_t bcr = 0, dcr = 0;

        /* Повторний старт перед кожним раундом арбітражу */
        hw_i3c_start_open_drain();
        if (!hw_i3c_write_byte_od((I3C_BROADCAST_ADDR << 1) | 0x01)) {
            break; /* Жоден ведений не відгукнувся - DAA завершено */
        }

        /* Зчитування 48 бітів PID + BCR + DCR переможця арбітражу */
        if (!hw_i3c_read_pid_bcr_dcr(&pid, &bcr, &dcr)) {
            break;
        }

        /* Призначення унікальної 7-бітної динамічної адреси */
        uint8_t assigned_addr = ctx->next_free_addr++;
        if (!hw_i3c_assign_addr_od(assigned_addr << 1)) {
            hw_i3c_stop_open_drain();
            return I3C_STATUS_NACK;
        }

        /* Збереження дескриптора пристрою в таблиці контролера */
        i3c_target_desc_t *dev = &ctx->targets[ctx->target_count++];
        dev->provisional_id = pid;
        dev->bcr = bcr;
        dev->dcr = dcr;
        dev->dynamic_addr = assigned_addr;
        dev->ibi_enabled = (bcr & 0x02) != 0;
    }

    hw_i3c_stop_open_drain();
    return (ctx->target_count > 0) ? I3C_STATUS_OK : I3C_STATUS_NO_DEVICES;
}

i3c_status_t i3c_handle_ibi(i3c_bus_context_t *ctx, uint8_t *winning_addr,
                            uint8_t *mdb) 
{
    if (!ctx || !winning_addr || !mdb) return I3C_STATUS_BUS_LOST;

    /* Контролер фіксує перехід SDA в '0' при SCL=1 під час спокою */
    uint8_t addr_byte = 0;
    extern bool hw_i3c_clock_ibi_arbitration(uint8_t *addr_out);
    if (!hw_i3c_clock_ibi_arbitration(&addr_byte)) {
        return I3C_STATUS_BUS_LOST;
    }

    uint8_t target_addr = addr_byte >> 1;
    *winning_addr = target_addr;

    /* Знаходимо пристрій у реєстрі для перевірки підтримки корисного навантаження */
    bool has_payload = false;
    for (size_t i = 0; i < ctx->target_count; ++i) {
        if (ctx->targets[i].dynamic_addr == target_addr) {
            has_payload = (ctx->targets[i].bcr & 0x04) != 0;
            break;
        }
    }

    /* Відправляємо ACK на лінії відкритого стоку */
    extern void hw_i3c_send_ack(void);
    hw_i3c_send_ack();

    /* Зчитуємо обов'язковий байт даних переривання (MDB) */
    if (has_payload) {
        extern uint8_t hw_i3c_read_byte_with_t_bit(bool *is_last);
        bool is_last = false;
        *mdb = hw_i3c_read_byte_with_t_bit(&is_last);
    } else {
        *mdb = 0x00;
    }

    hw_i3c_stop_open_drain();
    return I3C_STATUS_OK;
}
```
```cpp
// i3c_dispatcher.cpp - Обробка подій та реєстрація переривань цілей на C++20
#include "i3c_controller.hpp"
#include <iostream>
#include <functional>
#include <unordered_map>

namespace mipi::i3c {

using IbiCallback = std::function<void(uint8_t dynamic_addr, uint8_t mdb)>;

class IbiEventDispatcher {
public:
    explicit IbiEventDispatcher(BusController& bus) noexcept : bus_(bus) {}

    void register_handler(uint8_t dynamic_address, IbiCallback callback) {
        callbacks_[dynamic_address] = std::move(callback);
    }

    [[nodiscard]] std::expected<void, Status> process_pending_ibi() noexcept {
        uint8_t winning_addr = 0;
        uint8_t mdb_value = 0;

        // Виклик низькорівневого захоплення IBI на шині
        if (auto res = capture_ibi_event(winning_addr, mdb_value); !res) {
            return std::unexpected(res.error());
        }

        if (auto it = callbacks_.find(winning_addr); it != callbacks_.end()) {
            it->second(winning_addr, mdb_value);
        }

        return {};
    }

private:
    [[nodiscard]] std::expected<void, Status> capture_ibi_event(
        uint8_t& out_addr, uint8_t& out_mdb) noexcept 
    {
        // Імітація захоплення апаратного переривання шини
        out_addr = 0x08;
        out_mdb = 0x01; // Data Ready флаг акселерометра
        return {};
    }

    BusController& bus_;
    std::unordered_map<uint8_t, IbiCallback> callbacks_;
};

} // namespace mipi::i3c
```
:::

---

### Інтеграція в операційні системи реального часу (RTOS) та обробка потоків

У багатозадачних середовищах (FreeRTOS, Zephyr RTOS, NuttX) драйвер шини I3C організовується як централізований сервіс з чергою повідомлень та асинхронним диспетчером:

1. **Ізоляція контексту переривань (ISR):** Обробник апаратного переривання контролера I3C, який спрацьовує при виявленні спаду на лінії SDA у стані спокою, виконує лише швидке вичитування адреси та байта MDB у кільцевий буфер переривань без блокування системного шедулера.
2. **Диспетчеризація завдань (Deferred Work / Event Task):** Після прийому байта MDB обробник ISR надсилає семафор або повідомлення в чергу потоку `i3c_event_thread`. Цей потік десеріалізує тип події (наприклад, готовність даних компаса чи барометра) та викликає зареєстрований зворотний виклик користувацького драйвера.
3. **Синхронізація доступу:** Усі звичайні операції зчитування та запису SDR/HDR захищаються м'ютексом шини `k_mutex` або `xSemaphoreCreateMutex()`. Це запобігає перетину фонових транзакцій передачі блоків даних із циклами обробки термінових переривань IBI.

---

### Апаратні пастки та рекомендації з реалізації драйвера

1. **Фазові таймаути перемикання Open-Drain → Push-Pull:** Під час переходу від фази адреси до передачі корисних байтів драйвер зобов'язаний витримати затримку стабілізації лінії (*Bus Handover Delay*). Якщо верхній транзистор увімкнеться до того, як відпущена лінія SDA досягне рівня не менше 0.7 VDD через підтяжку, виникає стрибок наскрізного струму, здатний пошкодити захисні ESD-діоди вхідних буферів.
2. **Арбітражний конфлікт за адресою 7'h7E:** Коли контролер намагається почати передачу команди CCC, виставляючи адресу `0x7E`, цільовий пристрій може одночасно розпочати запит IBI або Hot-Join, притягуючи лінію до нуля на 2-му або 3-му біті адреси. Драйвер контролера зобов'язаний постійно моніторити фактичний стан лінії SDA. Якщо виявлено розбіжність, контролер повинен негайно припинити видачу бітів `0x7E`, визнати поразку в арбітражі й перейти в режим прийому переривання цілі.
3. **Обробка помилок T-біта парності:** Якщо під час прийому байта у режимі SDR виявлено порушення парності T-біта, контролер не перериває поточну транзакцію аварійним сигналом STOP, оскільки це може збити внутрішній конвеєр FIFO веденого пристрою. Замість цього драйвер маркує весь прийнятий пакет як пошкоджений і запитує повторне читання після завершення поточної пачки.
4. **Аварійне відновлення заблокованої шини:** Якщо ведений чип через електростатичний розряд зависає у стані притягування лінії SDA до нуля, контролер перемикає вивід SCL у режим програмного керування GPIO (*Bit-Banging*) і генерує 9 послідовних імпульсів з періодом 5 мкс. Отримавши 9 тактових фронтів без підтвердження, внутрішній кінцевий автомат цілі примусово скидається і звільняє лінію SDA у стан високого імпедансу.
