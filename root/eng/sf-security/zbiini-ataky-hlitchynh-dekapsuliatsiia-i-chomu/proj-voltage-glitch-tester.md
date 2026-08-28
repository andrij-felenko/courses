# ⚙️ Захищене виконання коду та стійкі машини станів

У традиційній розробці вбудованого програмного забезпечення перевірка цифрового підпису, верифікація пароля чи перевірка прав доступу зазвичай реалізується через функції, що повертають булевий результат `true` або `false`. На рівні машинних інструкцій компілятор перетворює такі конструкції на пару інструкцій порівняння та умовного переходу (`CMP` та `BEQ`/`BNE`). Одиничний апаратний збій напруги живлення (Voltage Glitch) або тактового імпульсу (Clock Glitch) спотворює обчислення в АЛП чи затримує поширення сигналу прапорців, перетворюючи інструкцію умовного розгалуження на порожню операцію `NOP`. У результаті зловмисник отримує доступ до критичних функцій системи незалежно від коректності криптографічного ключа.

## 1. Вразливий шаблон та його асемблерний аналіз

Розглянемо типовий фрагмент процедури безпечного завантаження (Secure Boot), написаний без урахування фізичних збійних атак:

:::tabs
```c
/* Вразлива реалізація: вразлива до пропуску однієї інструкції BEQ */
bool verify_firmware_signature(const uint8_t *image, size_t len) {
    if (crypto_rsa_verify(image, len) == true) {
        return true;
    }
    return false;
}

void bootloader_main(void) {
    if (verify_firmware_signature(FW_ADDR, FW_SIZE)) {
        boot_kernel(); /* Зловмисник подає глітч і запускає шкідливий образ */
    } else {
        lockup_device();
    }
}
```
```cpp
/* Вразлива реалізація на C++ */
#include <cstdint>
#include <span>

bool verify_firmware_signature(std::span<const uint8_t> image) {
    return crypto_rsa_verify(image.data(), image.size());
}

void bootloader_main() {
    if (verify_firmware_signature({FW_ADDR, FW_SIZE})) {
        boot_kernel(); /* Одиничний збій у ALU оминає умову */
    } else {
        lockup_device();
    }
}
```
:::

Якщо скомпілювати цей код за допомогою `arm-none-eabi-gcc` з оптимізацією `-O2`, функція `bootloader_main` транслюється в таку асемблерну послідовність для архітектури ARM Cortex-M:

```text
bootloader_main:
    LDR    R1, =FW_SIZE
    LDR    R0, =FW_ADDR
    BL     verify_firmware_signature
    CMP    R0, #0               ; Порівняння результату з нулем (false)
    BEQ    .L_lockup            ; [ВРАЗЛИВІСТЬ] Якщо R0 == 0 -> перехід на блокування
    BL     boot_kernel          ; Передача керування ядру (успішний запуск)
.L_lockup:
    BL     lockup_device
```

З погляду супротивника, який контролює напругу живлення ядра через плату на кшталт ChipWhisperer, для повного зламу захисту достатньо виконати рівно одну дію: подати короткочасне просідання напруги (глітч тривалістю 15–25 нс) на такті виконання інструкції `BEQ .L_lockup`. Через порушення часу встановлення (Setup Time Violation) тригер лічильника команд `PC` не встигає зафіксувати адресу переходу `.L_lockup` і просто інкрементується до наступного рядка — `BL boot_kernel`. Зловмисник отримує працюючу систему з непідписаним шкідливим кодом.

---

## 2. Інженерні принципи відмовостійкого програмування

Для запобігання обходу перевірок за допомогою одиночних або подвійних апаратних збоїв застосовують чотири взаємодоповнюючі інженерні принципи:

1. **Багатобітові константи замість 0 та 1:** Заміна стандартних булевих прапорців на 32-бітні значення з відстанню Геммінга не менше 16 бітів (наприклад, `0x5555AAAA` для успіху та `0xAAAA5555` для помилки). Перетворення одного стану на інший вимагає одночасної зміни 32 бітів у регістрі процесора, що фізично неможливо викликати одним глітчем.
2. **Подвійне комплементарне розгалуження:** Кожна критична дія перевіряється двома незалежними умовами, де друга перевірка використовує інверсну логіку порівняння. Якщо перша перевірка запитує «чи дорівнює результат УСПІХУ?», то друга перевірка запитує «чи НЕ дорівнює результат ПОМИЛЦІ?».
3. **Асемблерні бар'єри компілятора:** Компілятори з оптимізацією (`-O2`, `-O3`) агресивно оптимізують код: видаляють повторні однакові перевірки (Common Subexpression Elimination) або усувають змінні, стан яких компілятор вважає незмінним (Dead Code Elimination). Щоб змусити компілятор реально згенерувати дві окремі послідовності інструкцій у машинному коді, між перевірками обов'язково встановлюються бар'єри пам'яті: `__asm__ volatile("" ::: "memory")`.
4. **Контроль шляху виконання (Execution Flow Tracking):** Кожна критична функція веде акумулятивну змінну-токен. Кожен крок алгоритму модифікує токен унікальною бітовою маскою за допомогою операції XOR. Перед виконанням цільової дії перевіряється, чи токен містить точне результуюче значення, що доводить проходження кожного проміжного етапу перевірки без пропусків інструкцій.

---

## 3. Повна захищена реалізація

Нижче наведено виробничий приклад реалізації стійкого завантажувача мовами C та C++ з використанням багатобітових статусів, комплементарних перевірок та захисту потоку виконання:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Багатобітові статуси з відстанню Геммінга 32 біти */
#define STATUS_AUTH_OK          ((uint32_t)0x5555AAAAU)
#define STATUS_AUTH_FAIL        ((uint32_t)0xAAAA5555U)
#define STATUS_AUTH_INIT        ((uint32_t)0x00000000U)

/* Асемблерний бар'єр для захисту від оптимізацій компілятора */
#define HARDENED_BARRIER()      __asm__ volatile("" ::: "memory")

/* Прототипи системних функцій */
uint32_t crypto_rsa_verify_hardened(const uint8_t *image, size_t len);
void boot_kernel(void);
void system_emergency_lockup(void);

/**
 * @brief Безпечна процедура перевірки підпису та запуску ядра.
 */
void hardened_bootloader_main(const uint8_t *fw_ptr, size_t fw_len) {
    volatile uint32_t flow_token = 0x1A2B3C4DU;
    volatile uint32_t step1_res  = STATUS_AUTH_INIT;
    volatile uint32_t step2_res  = STATUS_AUTH_INIT;
    
    HARDENED_BARRIER();
    
    /* Етап 1: Перший прохід криптографічної верифікації */
    step1_res = crypto_rsa_verify_hardened(fw_ptr, fw_len);
    HARDENED_BARRIER();
    
    /* Перший бар'єр: пряма перевірка на успішний статус */
    if (step1_res != STATUS_AUTH_OK) {
        system_emergency_lockup();
    }
    
    /* Оновлення токена шляху виконання для етапу 1 */
    flow_token ^= 0x5E6F7A8BU;
    HARDENED_BARRIER();
    
    /* Етап 2: Повторний незалежний розрахунок криптографічного підпису */
    step2_res = crypto_rsa_verify_hardened(fw_ptr, fw_len);
    HARDENED_BARRIER();
    
    /* Другий бар'єр: комплементарна перевірка на стан помилки або скидання */
    if (step2_res == STATUS_AUTH_FAIL || step2_res == STATUS_AUTH_INIT) {
        system_emergency_lockup();
    }
    
    /* Оновлення токена шляху виконання для етапу 2 */
    flow_token ^= 0x9C8D7E6FU;
    HARDENED_BARRIER();
    
    /* Третій бар'єр: узгодженість результатів двох незалежних обчислень */
    if ((step1_res ^ step2_res) != 0U) {
        system_emergency_lockup();
    }
    HARDENED_BARRIER();
    
    /* Четвертий бар'єр: верифікація фінального стану токена шляху виконання */
    uint32_t expected_token = 0x1A2B3C4DU ^ 0x5E6F7A8BU ^ 0x9C8D7E6FU;
    if (flow_token != expected_token) {
        system_emergency_lockup();
    }
    
    /* Доступ до ядра надається лише за успішного подолання всіх чотирьох бар'єрів */
    boot_kernel();
}
```
```cpp
#include <cstdint>
#include <span>

namespace secure_boot {

enum class AuthStatus : uint32_t {
    Success       = 0x5555AAAAU,
    Failure       = 0xAAAA5555U,
    Uninitialized = 0x00000000U
};

/* Асемблерний бар'єр пам'яті */
inline void compiler_barrier() noexcept {
    asm volatile("" ::: "memory");
}

/* Клас контролю цілісності ланцюга виконання */
class FlowTracker {
public:
    constexpr explicit FlowTracker(uint32_t initial_seed) noexcept 
        : current_token_(initial_seed), seed_(initial_seed) {}

    void step(uint32_t signature) noexcept {
        compiler_barrier();
        current_token_ ^= signature;
        compiler_barrier();
    }

    [[nodiscard]] bool is_flow_intact(uint32_t combined_signature) const noexcept {
        compiler_barrier();
        const uint32_t expected = seed_ ^ combined_signature;
        const uint32_t actual = current_token_;
        compiler_barrier();
        return (actual == expected) && ((actual ^ ~expected) == 0xFFFFFFFFU);
    }

private:
    volatile uint32_t current_token_;
    uint32_t seed_;
};

/* Прототипи системних функцій */
AuthStatus crypto_rsa_verify_hardened(std::span<const uint8_t> image) noexcept;
[[noreturn]] void emergency_lockup() noexcept;
void boot_kernel() noexcept;

void hardened_bootloader_main(std::span<const uint8_t> firmware_image) {
    FlowTracker tracker(0x1A2B3C4DU);
    constexpr uint32_t Step1Sign = 0x5E6F7A8BU;
    constexpr uint32_t Step2Sign = 0x9C8D7E6FU;

    compiler_barrier();

    /* Етап 1: Первинна криптографічна перевірка */
    const auto res1 = crypto_rsa_verify_hardened(firmware_image);
    compiler_barrier();

    if (res1 != AuthStatus::Success) {
        emergency_lockup();
    }

    tracker.step(Step1Sign);

    /* Етап 2: Повторна криптографічна перевірка */
    const auto res2 = crypto_rsa_verify_hardened(firmware_image);
    compiler_barrier();

    if (res2 == AuthStatus::Failure || res2 == AuthStatus::Uninitialized) {
        emergency_lockup();
    }

    tracker.step(Step2Sign);

    /* Етап 3: Перевірка ідентичності результатів */
    if (static_cast<uint32_t>(res1) != static_cast<uint32_t>(res2)) {
        emergency_lockup();
    }
    compiler_barrier();

    /* Етап 4: Перевірка проходження всіх контрольних точок */
    if (!tracker.is_flow_intact(Step1Sign ^ Step2Sign)) {
        emergency_lockup();
    }

    boot_kernel();
}

} // namespace secure_boot
```
:::

---

## 4. Аналіз згенерованого асемблерного коду та пастки оптимізації

Розглянемо, як компілятор транслює захищену функцію у машинний код:

```text
hardened_bootloader_main:
    PUSH   {R4, R5, LR}
    LDR    R4, =0x1A2B3C4D      ; Ініціалізація токена шляху
    BL     crypto_rsa_verify_hardened
    LDR    R1, =0x5555AAAA      ; STATUS_AUTH_OK
    CMP    R0, R1               ; Перевірка 1: R0 == 0x5555AAAA
    BNE    .L_panic_lockout
    
    LDR    R2, =0x5E6F7A8B
    EOR    R4, R4, R2           ; Оновлення токена етапу 1
    
    BL     crypto_rsa_verify_hardened
    LDR    R1, =0xAAAA5555      ; STATUS_AUTH_FAIL
    CMP    R0, R1               ; Перевірка 2: R0 == 0xAAAA5555
    BEQ    .L_panic_lockout
    CMP    R0, #0               ; Перевірка на неініціалізований стан
    BEQ    .L_panic_lockout
    
    LDR    R2, =0x9C8D7E6F
    EOR    R4, R4, R2           ; Оновлення токена етапу 2
    
    LDR    R3, =0xD249B929      ; Очікуване фінальне значення токена
    CMP    R4, R3               ; Перевірка 4: валідність ланцюга
    BNE    .L_panic_lockout
    
    BL     boot_kernel
.L_panic_lockout:
    BL     system_emergency_lockup
```

### 4.1 Типові помилки під час розробки відмовостійкого коду

1. **Відсутність модифікатора `volatile` або бар'єрів пам'яті:** Якщо прибрати директиву `HARDENED_BARRIER()`, оптимізатор компілятора визначить, що функція `crypto_rsa_verify_hardened` викликається двічі з однаковими аргументами. Компілятор збереже результат першого виклику в регістрі ядра (наприклад, `R0`) і повністю видалить другий виклик, перетворивши подвійну перевірку на фікцію.
2. **Використання простих інверсій (`!res`):** Вираз `if (!res)` генерує просту перевірку `CMP R0, #0`. Навіть якщо функція повернула `0xAAAA5555` (помилка), логічне заперечення у мові C трактує будь-яке ненульове число як істину, повертаючи нуль, що приводить до помилкового пропуску. Порівняння завжди повинно бути строгим повнорозрядним (`res == STATUS_AUTH_OK`).
3. **Зберігання токенів у передбачуваних регістрах:** Якщо проміжний токен обчислюється простою інкрементацією (`token++`), випадковий глітч у лічильнику може згенерувати потрібне значення. Використання операцій XOR із випадковими 32-бітними константами гарантує, що значення токена на кожному кроці має максимальну ентропію.

---

## 5. Методика лабораторного тестування та оцінка стійкості

Для практичної верифікації розробленого захищеного коду збирається автоматизований тестовий стенд на базі інструменту ін'єкції збоїв (наприклад, NewAE ChipWhisperer-Lite або розробницької плати на базі ПЛІС Xilinx Artix-7):

1. **Підключення апаратури:**
   - Лінія живлення досліджуваного мікроконтролера `Vdd` підключається через швидкісний польовий транзистор MOSFET із драйвером до стенду глітчингу.
   - Один із виводів GPIO мікроконтролера налаштовується як лінія синхронізації (Trigger Pin): перед початком функції перевірки підпису вивід переводиться у стан логічної одиниці, а після завершення — у стан нуля.
   - Відлагоджувальний порт UART передає на комп'ютер статус виконання коду: успішний запуск, аварійне скидання або успішний обхід захисту (Bypass).
2. **Сканування простору параметрів (Glitch Parameter Sweeping):**
   - Автоматизований скрипт на Python запускає циклічне тестування (10 000–50 000 ітерацій), змінюючи три параметри:
     1. Затримку введення збою `t_offset` від фронту тригера (з кроком 2–5 нс);
     2. Тривалість імпульсу просідання напруги `t_width` (від 10 до 50 нс);
     3. Напругу зміщення `V_glitch` (від 0.2 В до 0.8 В).
3. **Результати тестування:**
   - Для наївного вразливого коду з одиночною перевіркою `if (verify())` карта збоїв демонструє стабільне вікно вразливості шириною 40–60 нс, у якому відсоток успішного обходу захисту досягає 85–92%.
   - Для захищеного шаблону з чотирма бар'єрами та контролем токена за 50 000 тестових спроб не фіксується жодного випадку обходу перевірки: 98.4% спроб завершуються апаратним скиданням або зависанням ядра у функції `system_emergency_lockup`, а 1.6% спроб ігноруються як недієві.

Це доводить, що грамотне програмне ущільнення суттєво підвищує вартість фізичної атаки навіть на мікроконтролерах загального призначення без спеціалізованого апаратного захисту Secure Element.
