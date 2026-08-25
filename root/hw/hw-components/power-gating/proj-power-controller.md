# ⚙️ Апаратний контролер керування живленням: RTL-автомат станів та системний драйвер

<preknowlist>
- [Power gating і clock gating](root:hw-components/power-gating) — загальні принципи стробування такту, силових ключів, ізоляції та збереження стану.
- [Система-на-кристалі (SoC)](root:hw-components/system-on-chip) — архітектура інтерконекту та взаємодія процесора з блоками керування живленням (PMU).
</preknowlist>

Керування живленням та тактуванням сучасного функціонального блоку в складі НВІС (наприклад, графічного ядра GPU, нейроприскорювача NPU чи кластера процесорних ядер) є критичною операцією, що вимагає мікросекундної або навіть наносекундної точності. Будь-яке пряме керування силовими транзисторами з боку програмного забезпечення (наприклад, через несинхронізований запис окремих бітів у регістри загального призначення GPIO) неминуче призведе до апаратної катастрофи:
- Якщо силові ключі знеструмлять блок раніше, ніж увімкнуться комірки ізоляції, вихідні лінії опиняться в плаваючому стані й відкриють наскрізні струми (Crowbar Current) у міліампери на вхідних каскадах сусіднього Always-On домену;
- Якщо тактовий сигнал відновиться до повної стабілізації напруги на віртуальній шині живлення, динамічне перемикання логіки викличе вторинне просідання напруги та спотворить архітектурний стан регістрів;
- Якщо ініціювати вимкнення живлення в момент, коли блок виконує незавершену транзакцію на системній шині AXI/NoC, шинний інтерконект перейде в стан вічного очікування підтвердження (Deadlock).

Для гарантії абсолютної надійності керування живленням повністю делегують детермінованому апаратному кінцевому автомату — **апаратному секвенсеру живлення** (Hardware Power Sequencer / Controller), розташованому в невимиканому домені Always-On. Програмне забезпечення (драйвер ядра ОС або мікрокод PMU) лише виставляє цільовий запит на зміну стану, а весь багатоступеневий часовий протокол відпрацьовує апаратна логіка.

Нижче розібрано повний цикл проектування системи керування живленням: побудова шинного квитування низькоспоживаючих станів, проектування кінцевого автомата на рівні RTL мовою SystemVerilog, побудова карти регістрів, написання системних драйверів мовами C та C++, взаємодія з прошивкою ARM PSCI, інтеграція з підсистемами Runtime PM та DVFS ядра Linux, схемотехніка Always-On буферизації, тестопридатність (DFT), апаратна емуляція та процедури фізичного налагодження.

---

## 1. Протокол узгодження зі системною шиною (Шинне квитування LPI / Q-Channel)

Перед тим як апаратний автомат розпочне процедуру знеструмлення домену, необхідно гарантувати повне припинення обміну даними на системній шині AXI або внутрішньокристальній мережі Network-on-Chip (NoC). Якщо живлення вимкнеться під час очікування відповіді `RVALID` або `BVALID`, шинний комутатор заблокується назавжди.

Для безпечної зупинки інтерфейсу використовують стандартизований протокол низькоспоживаючого квитування **ARM Q-Channel** (або P-Channel):

```
       Контролер живлення (PMU)                 Керований IP-блок
                 │                                      │
                 │ ─── 1. QREQn = 0 (Запит на сон) ───► │
                 │                                      │ [ Завершення конвеєра ]
                 │                                      │ [ Спорожнення черг FIFO ]
                 │                                      │ [ Блокування нових AXI ]
                 │ ◄── 2. QACCEPTn = 0 (Готовність) ─── │
                 │                                      │
                 │ [ Запуск апаратного FSM живлення ]   │
```

1. **Запит на перехід у сон:** Контролер живлення скидає лінію `QREQn = 0`;
2. **Обробка запиту IP-блоком:** Блок припиняє прийом нових транзакцій із шини AXI, дочікується завершення всіх активних пакетних передавань (In-Flight Transactions) та виставляє підтвердження готовності `QACCEPTn = 0`;
3. **Відхилення запиту (`QDENYn`):** Якщо блок зайнятий критичною операцією (наприклад, апаратний DMA виконує копіювання кадру), він виставляє `QDENYn = 0`, змушуючи контролер відкласти вимкнення живлення;
4. **Запуск секвенсера:** Отримавши сигнал `QACCEPTn = 0`, контролер живлення переходить до виконання фізичного протоколу FSM.

---

## 2. Архітектура кінцевого автомата переходів (FSM State Flow)

Апаратний контролер послідовності станів живиться від постійної шини `VDD_AON` та синхронізується опорним тактовим сигналом `clk_aon` (зазвичай низькочастотний стабільний генератор 24–100 МГц).

Автомат реалізує суворо впорядкований спрямований граф станів, у якому кожен наступний крок дозволяється лише після виконання попереднього фізичного інваріанта.

```
                  ┌─────────────────────────────────────────────────┐
                  ▼                                                 │
            [ ST_ACTIVE ] ─────────────────────────┐                │
                  ▲                                │                │
                  │ (Power-Up Sequence)            │ (Power-Down)   │
                  │                                │                │
            [ ST_START_CLOCK ]                     ▼                │
                  ▲                         [ ST_STOP_CLOCK ]       │
                  │                                │                │
            [ ST_DISABLE_ISO ]                     ▼                │
                  ▲                        [ ST_SAVE_RETENTION ]    │
                  │                                │                │
            [ ST_RELEASE_RESET ]                   ▼                │
                  ▲                         [ ST_ENABLE_ISO ]       │
                  │                                │                │
            [ ST_RESTORE_RET ]                     ▼                │
                  ▲                         [ ST_ASSERT_RESET ]     │
                  │                                │                │
            [ ST_WAIT_VDD_STABLE ]                 ▼                │
                  ▲                         [ ST_ASSERT_SLEEP ]     │
                  │                                │                │
            [ ST_DEASSERT_SLEEP ]                  ▼                │
                  ▲                         [ ST_POWER_OFF ] ───────┘
                  │                                │
                  └────────────────────────────────┘
```

### Покроковий розбір станів послідовності Power-Down:
1. `ST_ACTIVE`: Домен повністю функціональний. Тактовий сигнал подається (`gate_clk_en = 1`), ізоляція відключена (`iso_en = 0`), скид знято (`domain_reset_n = 1`), силові ключі відкриті (`sleep_ctrl = 0`). Отримавши запит на вимкнення (`pwr_req = 0`), FSM розпочинає вимкнення;
2. `ST_STOP_CLOCK`: Контролер скидає сигнал дозволу тактування `gate_clk_en = 0` на кореневих комірках ICG. Протягом одного такту тактове дерево заморожується, конвеєри зупиняються, усуваючи будь-яку динамічну активність та перехідні процеси в логіці;
3. `ST_SAVE_RETENTION`: Контролер генерує активний імпульс `retention_save = 1` тривалістю `PULSE_WIDTH_CYCLES` тактів. Усі архітектурні тригери переписують свій поточний логічний стан у тіньові Balloon-защіпки на Always-On живленні;
4. `ST_ENABLE_ISO`: Вмикається сигнал ізоляції `iso_en = 1`. Спеціальні комірки ізоляції на границях домену примусово фіксують усі вихідні лінії в безпечних станах (0 або 1), запобігаючи проникненню шумів та наскрізних струмів у сусідні блоки;
5. `ST_ASSERT_RESET`: Контролер примусово переводить лінію скидання комутованого домену в активний стан (`domain_reset_n = 0`). Це гарантує, що при майбутньому відновленні живлення схема не почне спонтанне неконтрольоване виконання інструкцій;
6. `ST_ASSERT_SLEEP`: Сигнал сну `sleep_ctrl = 1` передається на ланцюжок силових ключів. Транзистори сну закриваються, знеструмлюючи віртуальну шину `VDD_VIRTUAL`;
7. `ST_POWER_OFF`: Домен повністю знеструмлений. Контролер виставляє сигнал квитування `pwr_ack = 1`, повідомляючи процесор про успішний перехід у режим нульового статичного споживання.

### Покроковий розбір станів послідовності Power-Up:
1. `ST_DEASSERT_SLEEP`: Отримавши запит на пробудження (`pwr_req = 1`), контролер скидає сигнал сну `sleep_ctrl = 0`. Силові ключі починають послідовно відкриватися через буфери затримки Daisy Chain;
2. `ST_WAIT_VDD_STABLE`: Контролер запускає апаратний таймер на `WAKEUP_WAIT_CYCLES` тактів (або очікує сигнал від аналогового компаратора Power-Good). Цей інтервал необхідний для плавного заряду віртуальної ємності `C_v` та затухання коливань напруги;
3. `ST_RESTORE_RET`: Щойно напруга досягає номіналу, генерується імпульс `retention_restore = 1`, який переписує збережений контекст із Balloon-защіпок назад у робочі D-тригери;
4. `ST_RELEASE_RESET`: Знімається сигнал апаратного скиду (`domain_reset_n = 1`);
5. `ST_DISABLE_ISO`: Сигнал `iso_en` повертається в 0, відкриваючи проходження логічних сигналів крізь межу доменів;
6. `ST_START_CLOCK`: Відновлюється тактування через комірки ICG (`gate_clk_en = 1`). Автомат повертається в стан `ST_ACTIVE` і виставляє квитування готовності `pwr_ack = 1`.

---

## 3. Повний синтезований модуль секвенсера мовою SystemVerilog

```systemverilog
// Модуль апаратного контролера послідовності станів живлення
module power_domain_controller #(
    parameter int WAKEUP_WAIT_CYCLES = 16, // Таймаут стабілізації VDD (тактових циклів)
    parameter int PULSE_WIDTH_CYCLES = 2   // Тривалість імпульсів Save/Restore
)(
    input  logic clk_aon,          // Тактовий сигнал Always-On домену
    input  logic rst_aon_n,        // Асинхронний скид Always-On контролера
    
    // Програмний інтерфейс зв'язку з процесором або PMU
    input  logic pwr_req,          // 1 = Запит на увімкнення, 0 = Запит на вимкнення
    output logic pwr_ack,          // 1 = Поточний цільовий стан повністю встановлено
    output logic [3:0] cur_state,  // Телеметрія: поточний стан автомата FSM
    
    // Фізичні вихідні сигнали керування доменом
    output logic gate_clk_en,      // Дозвіл тактування для комірок ICG
    output logic iso_en,           // Керування комірками ізоляції (1 = ізоляція)
    output logic retention_save,   // Імпульс запису в Balloon-защіпки
    output logic retention_restore,// Імпульс зчитування з Balloon-защіпок
    output logic domain_reset_n,   // Скид логіки комутованого домену
    output logic sleep_ctrl        // Сигнал керування силовими ключами сну
);

    typedef enum logic [3:0] {
        ST_ACTIVE          = 4'd0,
        ST_STOP_CLOCK      = 4'd1,
        ST_SAVE_RETENTION  = 4'd2,
        ST_ENABLE_ISO      = 4'd3,
        ST_ASSERT_RESET    = 4'd4,
        ST_ASSERT_SLEEP    = 4'd5,
        ST_POWER_OFF       = 4'd6,
        ST_DEASSERT_SLEEP  = 4'd7,
        ST_WAIT_VDD_STABLE = 4'd8,
        ST_RESTORE_RET     = 4'd9,
        ST_RELEASE_RESET   = 4'd10,
        ST_DISABLE_ISO     = 4'd11,
        ST_START_CLOCK     = 4'd12
    } pwr_state_t;

    pwr_state_t state_reg, state_next;
    logic [7:0] timer_reg, timer_next;

    assign cur_state = state_reg;

    // Логіка переходів скінченного автомата
    always_comb begin
        state_next = state_reg;
        timer_next = timer_reg;

        case (state_reg)
            ST_ACTIVE: begin
                if (!pwr_req) begin
                    state_next = ST_STOP_CLOCK;
                    timer_next = '0;
                end
            end

            // --- Послідовність Power-Down ---
            ST_STOP_CLOCK: begin
                state_next = ST_SAVE_RETENTION;
                timer_next = '0;
            end

            ST_SAVE_RETENTION: begin
                if (timer_reg >= (PULSE_WIDTH_CYCLES - 1)) begin
                    state_next = ST_ENABLE_ISO;
                    timer_next = '0;
                end else begin
                    timer_next = timer_reg + 1'b1;
                end
            end

            ST_ENABLE_ISO: begin
                state_next = ST_ASSERT_RESET;
            end

            ST_ASSERT_RESET: begin
                state_next = ST_ASSERT_SLEEP;
            end

            ST_ASSERT_SLEEP: begin
                state_next = ST_POWER_OFF;
            end

            ST_POWER_OFF: begin
                if (pwr_req) begin
                    state_next = ST_DEASSERT_SLEEP;
                    timer_next = '0;
                end
            end

            // --- Послідовність Power-Up ---
            ST_DEASSERT_SLEEP: begin
                state_next = ST_WAIT_VDD_STABLE;
                timer_next = '0;
            end

            ST_WAIT_VDD_STABLE: begin
                if (timer_reg >= (WAKEUP_WAIT_CYCLES - 1)) begin
                    state_next = ST_RESTORE_RET;
                    timer_next = '0;
                end else begin
                    timer_next = timer_reg + 1'b1;
                end
            end

            ST_RESTORE_RET: begin
                if (timer_reg >= (PULSE_WIDTH_CYCLES - 1)) begin
                    state_next = ST_RELEASE_RESET;
                    timer_next = '0;
                end else begin
                    timer_next = timer_reg + 1'b1;
                end
            end

            ST_RELEASE_RESET: begin
                state_next = ST_DISABLE_ISO;
            end

            ST_DISABLE_ISO: begin
                state_next = ST_START_CLOCK;
            end

            ST_START_CLOCK: begin
                state_next = ST_ACTIVE;
            end

            default: state_next = ST_ACTIVE;
        endcase
    end

    // Формування вихідних керуючих сигналів (безглітчева комбінаційна логіка)
    always_comb begin
        // Безпечні значення за замовчуванням
        gate_clk_en       = 1'b0;
        iso_en            = 1'b1;
        retention_save    = 1'b0;
        retention_restore = 1'b0;
        domain_reset_n    = 1'b0;
        sleep_ctrl        = 1'b1;
        pwr_ack           = 1'b0;

        case (state_reg)
            ST_ACTIVE: begin
                gate_clk_en    = 1'b1;
                iso_en         = 1'b0;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
                pwr_ack        = 1'b1;
            end

            ST_STOP_CLOCK: begin
                gate_clk_en    = 1'b0;
                iso_en         = 1'b0;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
            end

            ST_SAVE_RETENTION: begin
                retention_save = 1'b1;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
            end

            ST_ENABLE_ISO: begin
                iso_en         = 1'b1;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
            end

            ST_ASSERT_RESET: begin
                iso_en         = 1'b1;
                domain_reset_n = 1'b0;
                sleep_ctrl     = 1'b0;
            end

            ST_ASSERT_SLEEP, ST_POWER_OFF: begin
                iso_en         = 1'b1;
                domain_reset_n = 1'b0;
                sleep_ctrl     = 1'b1;
                pwr_ack        = (state_reg == ST_POWER_OFF);
            end

            ST_DEASSERT_SLEEP, ST_WAIT_VDD_STABLE: begin
                iso_en         = 1'b1;
                domain_reset_n = 1'b0;
                sleep_ctrl     = 1'b0;
            end

            ST_RESTORE_RET: begin
                iso_en            = 1'b1;
                domain_reset_n    = 1'b0;
                sleep_ctrl        = 1'b0;
                retention_restore = 1'b1;
            end

            ST_RELEASE_RESET: begin
                iso_en         = 1'b1;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
            end

            ST_DISABLE_ISO, ST_START_CLOCK: begin
                iso_en         = 1'b0;
                domain_reset_n = 1'b1;
                sleep_ctrl     = 1'b0;
            end
        endcase
    end

    // Синхронний регістр збереження стану
    always_ff @(posedge clk_aon or negedge rst_aon_n) begin
        if (!rst_aon_n) begin
            state_reg <= ST_ACTIVE;
            timer_reg <= '0;
        end else begin
            state_reg <= state_next;
            timer_reg <= timer_next;
        end
    end

endmodule
```

---

## 4. Системний драйвер керування доменами живлення (Firmware Driver)

На рівні ядра операційної системи або низькорівневого коду енергоменеджменту (Firmware Power Manager) процесор взаємодіє з апаратними секвенсерами через адресний простір регістрів PMU (Power Management Unit).

### Реєстрова карта інтерфейсу PMU:
- `REG_PWR_REQ(domain)`: Регістр запиту стану (Write: 1 = увімкнути живлення, 0 = вимкнути живлення);
- `REG_PWR_STAT(domain)`: Регістр статусу (Read: Bit 0 = `ACK` завершення операції, Bit 1 = `BUSY` виконання переходу, Bits [5:2] = код поточного стану FSM).

У високонавантажених вбудованих системах керування живленням має бути не лише швидким, а й потокобезпечним та стійким до апаратних таймаутів.

Нижче наведено дві еквівалентні, ідіоматичні реалізації драйвера: мовою C для низькорівневого ядра/RTOS та мовою C++ з використанням сучасного стандарту C++23 (типізовані переліки, `std::expected` для обробки помилок та RAII-патерн захисту ресурсів).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define PMU_BASE_ADDR        0x4000E000U
#define REG_PWR_REQ(domain)  (*(volatile uint32_t*)(PMU_BASE_ADDR + 0x10U + ((domain) * 8U)))
#define REG_PWR_STAT(domain) (*(volatile uint32_t*)(PMU_BASE_ADDR + 0x14U + ((domain) * 8U)))

#define PWR_STATUS_ACK_MASK  (1U << 0)
#define PWR_STATUS_BUSY_MASK (1U << 1)
#define PWR_TIMEOUT_CYCLES   100000U

typedef enum {
    PWR_DOMAIN_GPU  = 0,
    PWR_DOMAIN_NPU  = 1,
    PWR_DOMAIN_DSP  = 2,
    PWR_DOMAIN_MAX  = 3
} power_domain_id_t;

typedef enum {
    PWR_ERR_OK      =  0,
    PWR_ERR_TIMEOUT = -1,
    PWR_ERR_INVALID = -2
} power_status_t;

/**
 * Переведення домену живлення у вказаний стан (увімкнено / вимкнено)
 * із контролем апаратного квитування та захистом від зависання.
 */
power_status_t power_domain_set_state(power_domain_id_t domain, bool enable) {
    if (domain >= PWR_DOMAIN_MAX) {
        return PWR_ERR_INVALID;
    }

    // Запис цільового запиту в апаратний регістр PMU
    REG_PWR_REQ(domain) = enable ? 1U : 0U;

    // Очікування квитування від апаратного автомата FSM
    uint32_t timeout = PWR_TIMEOUT_CYCLES;
    while (timeout > 0) {
        uint32_t status = REG_PWR_STAT(domain);
        if ((status & PWR_STATUS_ACK_MASK) != 0U && (status & PWR_STATUS_BUSY_MASK) == 0U) {
            return PWR_ERR_OK;
        }
        timeout--;
    }

    return PWR_ERR_TIMEOUT;
}
```
```cpp
#include <cstdint>
#include <expected>
#include <span>
#include <chrono>

enum class PowerDomain : uint32_t {
    Gpu = 0,
    Npu = 1,
    Dsp = 2,
    Max
};

enum class PowerError {
    Timeout,
    InvalidDomain,
    HardwareFault
};

class PowerManager {
public:
    static constexpr uintptr_t PmuBaseAddr = 0x4000E000U;

    static std::expected<void, PowerError> setDomainPower(PowerDomain domain, bool enable) noexcept {
        if (domain >= PowerDomain::Max) {
            return std::unexpected(PowerError::InvalidDomain);
        }

        const auto domainIdx = static_cast<uint32_t>(domain);
        auto* const reqReg  = reinterpret_cast<volatile uint32_t*>(PmuBaseAddr + 0x10U + (domainIdx * 8U));
        auto* const statReg = reinterpret_cast<const volatile uint32_t*>(PmuBaseAddr + 0x14U + (domainIdx * 8U));

        // Ініціація апаратного переходу FSM
        *reqReg = enable ? 1U : 0U;

        // Полінг підтвердження стабілізації домену з лімітом спроб
        constexpr uint32_t MaxAttempts = 100'000U;
        constexpr uint32_t AckMask     = (1U << 0);
        constexpr uint32_t BusyMask    = (1U << 1);

        for (uint32_t i = 0; i < MaxAttempts; ++i) {
            const uint32_t status = *statReg;
            if ((status & AckMask) != 0U && (status & BusyMask) == 0U) {
                return {};
            }
        }

        return std::unexpected(PowerError::Timeout);
    }
};

/**
 * RAII-обгортка для безпечного виконання обчислень у виділеному домені живлення.
 * Автоматично вмикає живлення при створенні об'єкта та гарантує
 * безпечне вимкнення живлення при виході зі скоупу функцій.
 */
class ScopedPowerDomain {
public:
    explicit ScopedPowerDomain(PowerDomain domain) 
        : domain_(domain), active_(false) {
        if (PowerManager::setDomainPower(domain_, true).has_value()) {
            active_ = true;
        }
    }

    ~ScopedPowerDomain() noexcept {
        if (active_) {
            PowerManager::setDomainPower(domain_, false);
        }
    }

    [[nodiscard]] bool isReady() const noexcept { return active_; }

    ScopedPowerDomain(const ScopedPowerDomain&) = delete;
    ScopedPowerDomain& operator=(const ScopedPowerDomain&) = delete;
    ScopedPowerDomain(ScopedPowerDomain&& other) noexcept 
        : domain_(other.domain_), active_(other.active_) {
        other.active_ = false;
    }

private:
    PowerDomain domain_;
    bool active_;
};
```
:::

---

## 5. Взаємодія з прошивкою ARM PSCI (Power State Coordination Interface)

У сучасних 64-розрядних архітектурах ARM Cortex-A керування живленням процесорних ядер стандартизовано специфікацією **ARM PSCI**. Операційна система (наприклад, Linux) не взаємодіє з регістрами PMU безпосередньо:

1. **Виклик Secure Monitor:** Ядро ОС виконує асемблерну інструкцію `HVC` (Hypervisor Call) або `SMC` (Secure Monitor Call), викликаючи прошивку вищого рівня привілеїв EL3 (ARM Trusted Firmware, ATF);
2. **Функції PSCI:** Прошивка обробляє запити `CPU_SUSPEND`, `CPU_OFF` або `SYSTEM_SUSPEND`;
3. **Координація когерентності (CCI / CMN):** Перед вимкненням живлення ядра прошивка видає команди скидання кеш-пам'яті L1/L2 (Clean & Invalidate), вимикає ядро з протоколу когерентності шини та записує запит у відповідний FSM-секвенсер.

---

## 6. Інтеграція з підсистемами Runtime PM та DVFS ядра Linux

У драйверах периферійних блоків на базі Linux керування доменами живлення повністю інтегроване в підсистему **Runtime Power Management (Runtime PM)** та механізм динамічного масштабування напруги й частоти (DVFS / `devfreq`):

1. **Опис дерева живлення в Device Tree (DTS):**
   У файлі опису апаратури домен оголошується як постачальник живлення, а керований пристрій прив'язується до нього через властивість `power-domains`:
   ```dts
   pmu: power-controller@4000e000 {
       compatible = "vendor,soc-pmu";
       reg = <0x4000e000 0x1000>;
       #power-domain-cells = <1>;
   };

   gpu: gpu@50000000 {
       compatible = "vendor,soc-gpu";
       reg = <0x50000000 0x10000>;
       power-domains = <&pmu 0>; /* PWR_DOMAIN_GPU */
   };
   ```
2. **Керування живленням у драйвері пристрою:**
   Драйвер графічного ядра не викликає низькорівневі регістри PMU напряму. Замість цього він використовує лічильник використання підсистеми Runtime PM:
   - Перед початком рендерингу кадру драйвер викликає `pm_runtime_get_sync(dev)`, що змушує ядро Linux ініціювати апаратне пробудження домену через FSM-секвенсер;
   - Після завершення обробки кадру драйвер викликає `pm_runtime_put_autosuspend(dev)`. Ядро запускає таймер автозасинання (наприклад, 50 мс). Якщо за цей час нових завдань не надійшло, підсистема автоматично переводить домен у стан глибокого сну через `pm_runtime_suspend()`;
3. **Координація з регулятором напруги (PMIC DVFS):**
   Під час виходу зі сну підсистема DVFS спочатку подає команду зовнішньому регулятору PMIC на встановлення базової робочої напруги `V_dd`, дочікується сигналу Power-Good від стабілізатора, після чого запускає FSM секвенсера. Щойно домен переходить у `ST_ACTIVE`, фазовий автопідстроювач частоти (PLL) розблоковується і тактова частота плавно підвищується до максимуму.

---

## 7. Схемотехніка та топологія Always-On буферів (Always-On Buffer Cells)

Особливу увагу при проектуванні приділяють прокладанню керівних ліній, що проходять крізь територію вимиканого домену. Якщо сигнал керування `sleep_ctrl` або `iso_en` проходить через довгу металеву доріжку, на ній необхідно розміщувати проміжні повторювачі (буфери) для відновлення фронтів сигналу.

```
       [ Контролер Always-On ]
                 │
                 ├─── VDD_AON (Постійне живлення) ──────────────────────────┐
                 │                                                          │
                 ▼                                                          ▼
        [ AON-Буфер 1 ] ─── (Метал M4/M5) ───► [ AON-Буфер 2 ] ───► [ Силові ключі ]
                 │                                      │
        [ Ізольована кишеня N-Well ]           [ Ізольована кишеня N-Well ]
```

1. **Ізоляція підкладки та кишень (N-Well Isolation):**
   Буфери ліній керування повинні бути спеціальними комірками **AON Buffer**. Їхні n-кишені (N-Well) підключаються не до локальної шини `VDD_VIRTUAL`, а живляться від резервної шини `VDD_AON`. Навколо кожної такої комірки на топології формують захисні охоронні кільця (Guard Rings), що запобігають паразитній інжекції носіїв заряду та виникненню тиристорного ефекту замикання (Latch-up);
2. **Екранування металевих шарів (Shielding):**
   Провідники керуючих сигналів `sleep_ctrl` та `iso_en` прокладають на високих шарах металізації (M4–M6) і оточують з обох боків заземленими екрануючими лініями `GND Shield`. Це усуває ємнісні наведення (Crosstalk) від сусідніх сигнальних ліній, коли домен переходить у плаваючий стан сну.

---

## 8. Тестопридатність та діагностика на виробництві (DFT & Scan Chains)

Впровадження Power Gating вимагає модифікації загальної стратегії тестування кристала на кремнієвій фабриці (Design for Testability, DFT):

1. **Зшивання ланцюжків сканування (Scan Chain Stitching):**
   Ланцюжки тестових регістрів сканування (Scan Chains) не повинні хаотично перетинати межі різних доменів живлення. Якщо ланцюжок виходить із комутованого домену, на лінії послідовного сканування `Scan Out` обов'язково встановлюється комірка ізоляції;
2. **Тестування силових транзисторів (IDDQ Testing):**
   Для виявлення дефектів пробою або закорочення силових ключів застосовують вимірювання статичного струму спокою (IDDQ Test). Тестовий автомат переводить домен у стан `ST_POWER_OFF` і вимірює залишковий струм витоку: якщо струм перевищує мікроампери, силова сітка містить дефектний або закорочений ключ;
3. **Обхід стробування такту при тестуванні (Scan Enable Bypass):**
   Під час генерації тестових векторів ATPG сигнал тестового режиму `SE = 1` примусово відкриває всі комірки ICG, гарантуючи 100% покриття тригерів тестовими імпульсами.

---

## 9. Підводні камені, захисні інваріанти та крайові випадки

1. **Метастабільність на перетині доменів тактування (CDC — Clock Domain Crossing):**
   Сигнал запиту `pwr_req` формується високочастотним процесором у власному тактовому домені `clk_cpu` (наприклад, 2.5 ГГц), тоді як контролер живлення працює від повільного Always-On такту `clk_aon` (32 кГц або 24 МГц). Пряме підключення викличе метастабільність першого тригера FSM. На вході сигналу `pwr_req` обов'язково встановлюють двотригерний синхронізатор (2-FF Synchronizer);
2. **Фізична ізоляція та живлення буферів ліній керування:**
   Усі провідники керуючих сигналів (`iso_en`, `retention_save`, `sleep_ctrl`), що прокладаються від Always-On контролера крізь площу комутованого домену, повинні буферизуватися виключно комірками з живленням від `VDD_AON`. Якщо в ланцюг сигналу `sleep_ctrl` випадково потрапить стандартний буфер із живленням від `VDD_VIRTUAL`, при знеструмленні домену він знеструмить сам себе, втратить здатність тримати високий рівень на затворах силових ключів і спричинить хаотичне самовільне вмикання силової мережі;
3. **Запобігання перевантаженню по струму під час збереження стану (Retention Current Spike):**
   Одночасне перемикання сотень тисяч Balloon-защіпок під час імпульсу `SAVE` створює короткочасний сплеск струму на резервній шині `VDD_AON`. Для згладжування цього сплеску вздовж рядів Retention-тригерів обов'язково розміщують додаткові вбудовані блокувальні конденсатори (Decoupling Cells);
4. **Аварійний сценарій провалу живлення (Brown-Out Recovery):**
   Якщо під час виконання процедури збереження стану або ланцюжкового виходу зі сну напруга живлення `VDD` несподівано просідає нижче критичного порогу роботи схеми скидання (Power-On Reset, POR), апаратний контролер перериває виконання штатної послідовності, ігнорує відновлення Retention-даних, накладає безумовну ізоляцію та ініціює повне холодне скидання (Cold Reset) всього домену;
5. **Верифікація за допомогою формальних UPF-асерцій (SystemVerilog Assertions):**
   На етапі логічного моделювання RTL у симуляторі підключають power-aware розширення IEEE 1801. Спеціальні асерції SVA автоматично перевіряють виконання часових інваріантів:
   ```systemverilog
   // Асерція: ізоляція повинна бути активною завжди, коли живлення вимкнене
   property p_iso_during_powerdown;
       @(posedge clk_aon) (sleep_ctrl == 1'b1) |-> (iso_en == 1'b1);
   endproperty
   assert property (p_iso_during_powerdown) else $error("Порушення: знеструмлення без активної ізоляції!");
   ```
   Це дозволяє гарантовано виявити будь-яку розсинхронізацію сигналів ще до передачі топології на кремнієву фабрику;
6. **Апаратна емуляція на платформах Palladium/Zebu:**
   Перед передачею чіпа у виробництво UPF-стратегію верифікують на апаратних емуляторах НВІС (наприклад, Cadence Palladium або Synopsys Zebu). Емулятор апаратно моделює роботу силових ключів, комірок ізоляції та Balloon-тригерів під реальним навантаженням повної операційної системи Linux/Android на тактових частотах 1–5 МГц (що у мільйони разів швидше за програмні симулятори), дозволяючи протестувати сотні тисяч циклів засинання та пробудження домену під час завантаження графічного стека;
7. **Лабораторний Bring-Up та діагностика крайових збоїв:**
   Під час першого запуску прототипу кремнієвого чіпа в лабораторії проводять фізичне простеження перехідних процесів:
   - **Мікрозондування віртуальної шини:** За допомогою високочастотних активних зондів із низькою ємністю (< 0.1 пФ) знімають осцилограму `V_virtual(t)` під час пробудження, вимірюючи реальну швидкість наростання та амплітуду дзвону;
   - **Тепловізійний контроль емісії (EMMI):** Камери інфрачервоної емісійної мікроскопії дозволяють побачити локальні гарячі точки (Hotspots) на кристалі, що виникають при наскрізних струмах Crowbar у разі порушення послідовності ввімкнення ізоляції;
   - **Аналізатори спектру живлення:** Вимірювання високочастотного шуму на шинах VDD/VSS за допомогою аналізаторів спектру допомагає точно підібрати кількість ступенів Daisy Chain та налаштувати затримки буферів у фінальній ревізії кремнію.
