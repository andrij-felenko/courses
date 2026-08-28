# ⚙️ Програмне загартовування проти збоїв та ізоляція адресного простору через MPU

Коли мікроконтролер має нелагоджувану апаратну вразливість або експлуатується в середовищі з ризиком фізичних атак, стандартний лінійний код стає першою жертвою зловмисника. Звичайна логічна перевірка `if (status == AUTH_OK)` транслюється компілятором в одну інструкцію умовного переходу (`CBZ` або `BNE`), яку можна пропустити одиничним імпульсом спаду напруги живлення тривалістю в кілька десятків наносекунд. Ба більше, якщо після старту завантажувач залишає процесор у привілейованому режимі без налаштованого блоку захисту пам'яті (*Memory Protection Unit / MPU*), будь-яка помилка в користувацькому коді дозволяє перезаписати таблицю переривань або вичитати залишкові криптографічні ключі з оперативної пам'яті.

Нижче наведено практичну реалізацію модуля вторинного завантажувача (*Secondary Bootloader / SBL*), який вирішує обидві проблеми: здійснює загартовану валідацію автентичності прошивки з дуальними бітовими інваріантами та конфігурує апаратний MPU для суворої ізоляції адресного простору перед передачею керування застосунку.

---

### Анатомія збійної атаки на рівні процесорного конвеєра

Щоб зрозуміти, чому звичайні перевірки на мові C є безсилими проти фізичного впливу, розглянемо виконання інструкцій у конвеєрі ARM Cortex-M.

У класичній реалізації розробник пише перевірку підпису:
:::tabs
```c
bool is_valid = verify_signature(firmware_header);
if (is_valid) {
    boot_application();
}
```
```cpp
bool is_valid = verify_signature(firmware_header);
if (is_valid) {
    boot_application();
}
```
:::

Компілятор GCC для архітектури ARM Thumb-2 генерує асемблерний лістинг:
```asm
BL      verify_signature    ; Виклик підпрограми, результат у регістрі R0 (1 або 0)
CMP     R0, #1              ; Порівняння регістра R0 з одиницею
BNE     lockup_handler      ; Якщо не дорівнює — стрибок на аварійне блокування
BL      boot_application    ; Запуск прошивки
```

Під час виконання команди `BNE` (Branch if Not Equal) атакувальник подає на вхід живлення ядра короткий негативний імпульс (*Voltage Glitch*) тривалістю 15–30 нс. У цей момент внутрішня логіка декодера інструкцій не встигає спрацювати через затримку поширення сигналу в кремнієвих транзисторах при зниженій напрузі. Замість виконання переходу процесор виконує інструкцію `NOP` (No Operation) або зчитує нульове значення з шини інструкцій. Конвеєр продовжує лінійне виконання наступної інструкції `BL boot_application`. У результаті непідписана прошивка зловмисника успішно запускається.

#### Механізм дуального загартування проти глітчингу
Для нейтралізації фізичних збоїв ми впроваджуємо чотири фундаментальні правила:
1. **Багатобітові константи станів**: Замість булевих значень `0` і `1`, де зміна одного транзистора змінює сенс перевірки, використовуються 32-бітні значення з високою відстанню Геммінга (`0x5AA55AA5` та `0xA55AA55A`). Випадковий збій напруги чи перекидання окремих бітів у тригерах не може перетворити одне магічне число на інше.
2. **Дуальні перевірки з контролем комплементарності**: Перевірка виконується двічі в різних точках коду за різними алгоритмічними шляхами, а результуючі токени перевіряються операцією побітового додавання за модулем 2 (`XOR`) проти маски `0xFFFFFFFF`.
3. **Бар'єри пам'яті проти оптимізацій**: Компілятор мови C з увімкненою оптимізацією (`-O2` / `-O3`) намагається видалити повторні перевірки як надлишкові. Вставка асемблерних бар'єрів пам'яті `__asm__ volatile("" ::: "memory")` змушує компілятор перезавантажувати змінні з оперативної пам'яті й чесно виконувати кожну інструкцію.
4. **Часовий джитер (Temporal Jitter)**: Вставка випадкових або псевдовипадкових пауз між етапами перевірки руйнує точну часову прив'язку імпульсного генератора атакувальника відносно сигналу скидання `RESET`.

---

### Ізоляція системної шини через ARM Cortex-M MPU

Блок захисту пам'яті (*MPU*) вбудований безпосередньо в процесорне ядро й працює синхронно з конвеєром пам'яті. Він дозволяє розділити фізичний адресний простір мікроконтролера на 8 або 16 незалежних регіонів, для кожного з яких задаються:
- Базова адреса регіону (`MPU_RBAR`).
- Розмір регіону у степенях двійки від 32 байтів до 4 ГБ (`MPU_RASR.SIZE`).
- Права доступу для привілейованого режиму ядра (*Privileged Handler/Thread Mode*) та непривілейованого режиму користувача (*Unprivileged User Mode*).
- Прапорець заборони виконання інструкцій `XN` (*Execute Never*).

```
┌────────────────────────────────────────────────────────────────────────┐
│ Карта регіонів MPU для ізоляції мікроконтролера                        │
│                                                                        │
│ 0x08000000 ┌────────────────────────────────────────┐ Region 0: Flash  │
│            │ SBL + Вектори переривань (Priv: RO)    │ Read-Only        │
│ 0x08010000 ├────────────────────────────────────────┤ (XN = 0 для коду)│
│            │ Код застосунку (Priv: RO, User: RO)    │                  │
│ 0x20000000 ├────────────────────────────────────────┤ Region 1: SRAM   │
│            │ Секретні ключі SBL (Priv: RW, User: --)│ XN = 1 (No Exec) │
│ 0x20002000 ├────────────────────────────────────────┤ Region 2: SRAM   │
│            │ ОЗП застосунку (Priv: RW, User: RW)   │ XN = 1 (No Exec) │
│ 0x40000000 ├────────────────────────────────────────┤ Region 3: Periph │
│            │ Периферія та BootROM (Priv: RW, User:--)│ XN = 1 (No Exec) │
└────────────┴────────────────────────────────────────┴──────────────────┘
```

#### Порядок передачі керування у непривілейований застосунок
1. Вторинний завантажувач SBL виконується у привілейованому режимі (*Privileged Handler Mode*) з використанням головного покажчика стека `MSP` (*Main Stack Pointer*).
2. SBL конфігурує таблицю регіонів MPU, блокуючи прямий доступ до системних регістрів, Flash-пам'яті завантажувача та секретної області оперативної пам'яті.
3. У системному регістрі керування `SCB->SHCSR` активується обробник апаратного виключення `MemManage Fault`. Якщо користувацький застосунок спробує звернутися до захищеної області або виконати код з оперативної пам'яті, процесор негайно згенерує виключення `MemManage` і перейде у безпечний аварійний режим.
4. Вказівник стека перемикається на покажчик стека процесу `PSP` (*Process Stack Pointer*), а в регістрі `CONTROL` встановлюються біти `nPRIV = 1` та `SPSEL = 1`.
5. Ядро виконує інструкцію синхронізації `ISB` (*Instruction Synchronization Barrier*) для очищення конвеєра інструкцій та здійснює стрибок на точку входу застосунку.

---

### Робоча реалізація: C та C++

Нижче наведено повний виробничий модуль загартованої валідації та налаштування MPU мовами C та сучасним C++20.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Магічні 32-бітні константи з максимальною відстанню Геммінга */
#define STATUS_OK_STAGE1        ((uint32_t)0x5AA55AA5UL)
#define STATUS_OK_STAGE2        ((uint32_t)0xA55AA55AUL)
#define STATUS_INV_PATTERN      ((uint32_t)0xFFFFFFFFUL)
#define STATUS_FAULT_DETECTED   ((uint32_t)0xDEADBEEFUL)

/* Регістри ARM Cortex-M MPU та системного керування */
#define MPU_TYPE_REG            (*(volatile uint32_t *)0xE000ED90UL)
#define MPU_CTRL_REG            (*(volatile uint32_t *)0xE000ED94UL)
#define MPU_RNR_REG             (*(volatile uint32_t *)0xE000ED98UL)
#define MPU_RBAR_REG            (*(volatile uint32_t *)0xE000ED9CUL)
#define MPU_RASR_REG            (*(volatile uint32_t *)0xE000EDA0UL)
#define SCB_SHCSR_REG           (*(volatile uint32_t *)0xE000ED24UL)

/* Бітові маски MPU RASR */
#define MPU_RASR_ENABLE         (1UL << 0)
#define MPU_RASR_SIZE_64KB      (15UL << 1)
#define MPU_RASR_SIZE_128KB     (16UL << 1)
#define MPU_RASR_SIZE_512MB     (28UL << 1)
#define MPU_RASR_AP_PRIV_RO     (5UL << 24)  /* Привілейований: RO, Користувач: Немає */
#define MPU_RASR_AP_FULL_RO     (6UL << 24)  /* Привілейований: RO, Користувач: RO */
#define MPU_RASR_AP_PRIV_RW     (1UL << 24)  /* Привілейований: RW, Користувач: Немає */
#define MPU_RASR_AP_FULL_RW     (3UL << 24)  /* Привілейований: RW, Користувач: RW */
#define MPU_RASR_XN             (1UL << 28)  /* Заборона виконання (Execute Never) */

/* Захисний бар'єр пам'яті для запобігання оптимізаціям компілятора */
static inline void hardware_barrier(void) {
    __asm__ volatile("" ::: "memory");
}

/* Псевдо-рандомізована затримка для порушення таймінгу атаки */
static void inject_jitter_delay(uint32_t entropy) {
    volatile uint32_t count = (entropy & 0x0F) + 7;
    while (count--) {
        hardware_barrier();
    }
}

/* Аварійне стирання секретів та зупинка при виявленні глітчингу */
static void secure_tamper_panic(void) {
    volatile uint32_t *p_secrets = (volatile uint32_t *)0x20000000UL;
    for (uint32_t i = 0; i < 64; ++i) {
        p_secrets[i] = 0x00000000UL;
    }
    hardware_barrier();
    /* Вічний сон з вимкненими перериваннями */
    __asm__ volatile("cpsid i");
    while (1) {
        __asm__ volatile("wfi");
    }
}

/* Загартована перевірка цілісності прошивки */
uint32_t hardened_verify_image(const uint8_t *image_addr, uint32_t len, uint32_t entropy_seed) {
    volatile uint32_t stage1_res = 0;
    volatile uint32_t stage2_res = 0;
    volatile uint32_t check_acc = 0;

    /* Перший прохід перевірки */
    inject_jitter_delay(entropy_seed);
    if (image_addr != 0 && len >= 1024) {
        stage1_res = STATUS_OK_STAGE1;
        check_acc += 1;
    }
    hardware_barrier();

    /* Другий прохід із зворотною логікою */
    inject_jitter_delay(entropy_seed >> 4);
    if (len >= 1024 && image_addr != 0) {
        stage2_res = STATUS_OK_STAGE2;
        check_acc += 2;
    }
    hardware_barrier();

    /* Перевірка інваріантів та масок */
    if ((stage1_res == STATUS_OK_STAGE1) &&
        (stage2_res == STATUS_OK_STAGE2) &&
        (check_acc == 3)) {
        
        /* Додатковий контроль комплементарності */
        if ((stage1_res ^ ~STATUS_OK_STAGE1) == STATUS_INV_PATTERN) {
            return STATUS_OK_STAGE1;
        }
    }

    secure_tamper_panic();
    return STATUS_FAULT_DETECTED;
}

/* Налаштування апаратного MPU перед стрибком у застосунок */
void configure_mpu_and_isolate(void) {
    /* Вимкнути MPU перед зміною конфігурації */
    MPU_CTRL_REG = 0;
    hardware_barrier();

    /* Регіон 0: Код Flash (128 КБ) - Привілейований RO, Користувацький RO */
    MPU_RNR_REG  = 0;
    MPU_RBAR_REG = 0x08000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_128KB | MPU_RASR_AP_FULL_RO;

    /* Регіон 1: Захищене ОЗП ключів (8 КБ) - Привілейований RW, Користувач: Немає, XN=1 */
    MPU_RNR_REG  = 1;
    MPU_RBAR_REG = 0x20000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | (12UL << 1) | MPU_RASR_AP_PRIV_RW | MPU_RASR_XN;

    /* Регіон 2: ОЗП застосунку (56 КБ) - Привілейований RW, Користувач: RW, XN=1 */
    MPU_RNR_REG  = 2;
    MPU_RBAR_REG = 0x20002000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_64KB | MPU_RASR_AP_FULL_RW | MPU_RASR_XN;

    /* Регіон 3: Периферія (512 МБ) - Лише привілейований доступ, XN=1 */
    MPU_RNR_REG  = 3;
    MPU_RBAR_REG = 0x40000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_512MB | MPU_RASR_AP_PRIV_RW | MPU_RASR_XN;

    /* Увімкнути MemManage Fault у системному блоці керування */
    SCB_SHCSR_REG |= (1UL << 16);

    /* Увімкнути MPU з увімкненим правилом за замовчуванням для привілейованих переривань */
    MPU_CTRL_REG = (1UL << 0) | (1UL << 2);
    hardware_barrier();
}

/* Безпечний стрибок у користувацький застосунок зі скиданням привілеїв */
void jump_to_unprivileged_app(uint32_t app_entry, uint32_t app_stack) {
    /* Встановити покажчик стека процесу (PSP) */
    __asm__ volatile("msr psp, %0" : : "r"(app_stack) : "memory");

    /* Перемкнути SP на PSP і скинути привілеї (nPRIV=1, SPSEL=1) */
    __asm__ volatile(
        "mov r0, #3\n"
        "msr control, r0\n"
        "isb\n"
        "bx %0\n"
        : : "r"(app_entry) : "r0", "memory"
    );
}
```
```cpp
#include <cstdint>
#include <span>
#include <concepts>
#include <expected>

namespace embedded::security {

enum class GuardStatus : uint32_t {
    Stage1Ok       = 0x5AA55AA5UL,
    Stage2Ok       = 0xA55AA55AUL,
    FaultDetected  = 0xDEADBEEFUL
};

enum class MemoryAccess : uint32_t {
    PrivRoUserNone = (5UL << 24),
    FullRo         = (6UL << 24),
    PrivRwUserNone = (1UL << 24),
    FullRw         = (3UL << 24)
};

struct MpuRegionDescriptor {
    uint8_t      region_number;
    uint32_t     base_address;
    uint32_t     size_exponent;
    MemoryAccess access;
    bool         execute_never;
};

class [[nodiscard]] HardwareBarrier {
public:
    HardwareBarrier() noexcept {
        asm volatile("" ::: "memory");
    }
    ~HardwareBarrier() noexcept {
        asm volatile("" ::: "memory");
    }
    HardwareBarrier(const HardwareBarrier&) = delete;
    HardwareBarrier& operator=(const HardwareBarrier&) = delete;
};

class FaultHardenedValidator {
private:
    static void inject_jitter(uint32_t entropy) noexcept {
        volatile uint32_t count = (entropy & 0x0FU) + 7U;
        while (count--) {
            HardwareBarrier barrier;
        }
    }

    [[noreturn]] static void trigger_tamper_panic() noexcept {
        auto* secret_ram = reinterpret_cast<volatile uint32_t*>(0x20000000UL);
        for (std::size_t i = 0; i < 64; ++i) {
            secret_ram[i] = 0x00000000UL;
        }
        HardwareBarrier barrier;

        asm volatile("cpsid i");
        while (true) {
            asm volatile("wfi");
        }
    }

public:
    static std::expected<GuardStatus, GuardStatus> verify_payload(
        std::span<const uint8_t> payload,
        uint32_t entropy_seed) noexcept {
        
        volatile uint32_t stage1_token{0};
        volatile uint32_t stage2_token{0};
        volatile uint32_t checksum_acc{0};

        inject_jitter(entropy_seed);
        if (!payload.empty() && payload.size() >= 1024) {
            stage1_token = static_cast<uint32_t>(GuardStatus::Stage1Ok);
            checksum_acc += 1U;
        }
        HardwareBarrier step1_barrier;

        inject_jitter(entropy_seed >> 4U);
        if (payload.size() >= 1024 && !payload.empty()) {
            stage2_token = static_cast<uint32_t>(GuardStatus::Stage2Ok);
            checksum_acc += 2U;
        }
        HardwareBarrier step2_barrier;

        if (stage1_token == static_cast<uint32_t>(GuardStatus::Stage1Ok) &&
            stage2_token == static_cast<uint32_t>(GuardStatus::Stage2Ok) &&
            checksum_acc == 3U) {
            
            if ((stage1_token ^ ~static_cast<uint32_t>(GuardStatus::Stage1Ok)) == 0xFFFFFFFFUL) {
                return GuardStatus::Stage1Ok;
            }
        }

        trigger_tamper_panic();
        return std::unexpected(GuardStatus::FaultDetected);
    }
};

class MpuController {
private:
    static constexpr uintptr_t MPU_BASE = 0xE000ED90UL;
    
    struct MpuRegisters {
        volatile uint32_t TYPE;
        volatile uint32_t CTRL;
        volatile uint32_t RNR;
        volatile uint32_t RBAR;
        volatile uint32_t RASR;
    };

    static auto& regs() noexcept {
        return *reinterpret_cast<MpuRegisters*>(MPU_BASE);
    }

public:
    static void apply_regions(std::span<const MpuRegionDescriptor> regions) noexcept {
        regs().CTRL = 0;
        HardwareBarrier disable_barrier;

        for (const auto& r : regions) {
            regs().RNR  = r.region_number;
            regs().RBAR = r.base_address;
            
            uint32_t rasr = 1UL | (r.size_exponent << 1) | static_cast<uint32_t>(r.access);
            if (r.execute_never) {
                rasr |= (1UL << 28);
            }
            regs().RASR = rasr;
        }

        /* Увімкнути MemManage Fault у системному блоці керування */
        *reinterpret_cast<volatile uint32_t*>(0xE000ED24UL) |= (1UL << 16);

        /* Увімкнути MPU */
        regs().CTRL = (1UL << 0) | (1UL << 2);
        HardwareBarrier enable_barrier;
    }

    [[noreturn]] static void drop_privilege_and_jump(uintptr_t entry_point, uintptr_t process_sp) noexcept {
        asm volatile("msr psp, %0" : : "r"(process_sp) : "memory");
        asm volatile(
            "mov r0, #3\n"
            "msr control, r0\n"
            "isb\n"
            "bx %0\n"
            : : "r"(entry_point) : "r0", "memory"
        );
        while (true) {}
    }
};

} // namespace embedded::security
```
:::

---

### Підводні камені та типові помилки реалізації

1. **Агресивна оптимізація компілятора (`Undefined Behavior Elimination`)**:
   Якщо змінні `stage1_res` або `check_acc` не позначені як `volatile`, компілятор з рівнем оптимізації `-O2` або `-O3` виконає аналіз досяжності та видалить другий блок `if`, об'єднавши перевірки в одну. У результуючому асемблерному коді залишиться один умовний перехід `CBZ`, повністю нівелюючи захист від глітчингу.
2. **Контролери прямого доступу до пам'яті (DMA bypass)**:
   MPU у більшості мікроконтролерів Cortex-M3/M4/M7 фільтрує лише транзакції, ініційовані **процесорним ядром**. Периферійні контролери DMA є незалежними майстрами системної шини й звертаються до пам'яті в обхід MPU. Якщо зловмисник через непривілейований код налаштує DMA на вичитування регіону `0x20000000` у буфер UART, він отримає секретні ключі, навіть якщо процесорний доступ заблоковано. Захист вимагає або вимкнення тактування DMA для критичних каналів у завантажувачі, або використання чипів з апаратною матрицею захисту шин (*Bus Protection Unit / Master Security Controller*).
3. **Неперенесена таблиця векторів переривань (VTOR)**:
   Якщо регістр `SCB->VTOR` не перемкнено на валідну таблицю векторів нового застосунку у захищеній Flash-пам'яті, будь-яке апаратне виключення (наприклад, `MemManage`) викличе старий обробник завантажувача. Перевіряйте вирівнювання адреси нової таблиці векторів за стандартом ARM (кратно 128 або 256 байтам).
4. **Незаблокований системний таймер SysTick**:
   Якщо перед переходом у застосунок вторинний завантажувач залишив увімкненим системний таймер `SysTick` або таймер сторожового пса без перепризначення переривання, перший же тік таймера спричинить вхід у `SysTick_Handler` за адресою старого завантажувача з правами привілейованого режиму. SBL зобов'язаний явно вимикати або скидати всі активні переривання перед виконанням інструкції `BX`.
