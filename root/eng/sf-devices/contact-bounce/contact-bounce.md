# Брязкіт механічних контактів (Contact Bounce & Debouncing)

<preknowlist>
- [GPIO-регістри](root:sf-devices/gpio-registers) — принципи зчитування логічних рівнів виводів через вхідні регістри даних
- [Електричні налаштування виводів (Pad Control)](root:sf-devices/pad-control) — робота підтягувальних резисторів pull-up/pull-down та гістерезис вхідного тригера Шмітта
</preknowlist>

Під час замикання чи розмикання електромеханічних елементів (кнопок, тумблерів, реле, герконів) виникає фізичне явище пружного відскоку контакту — **брязкіт механічних контактів (Contact Bounce)**. Через пружність матеріалу та механічні коливання поверхні контактних пластин не замикаються миттєво, а проходять серію хаотичних мікрозамикань і розмикань тривалістю від $1\text{ мс}$ до $20\text{ мс}$.

Для високоефективних мікроконтролерів із частотою ядра десятки й сотні мегагерц кожен мікровідскок виглядає як окремий повноцінний логічний імпульс, що призводить до хибних повторних спрацьовувань, лавинних переривань та збоїв конечних автоматів.

---

## 1. Фізика перехідного процесу та електричний розрахунок RC-фільтра

Для придушення брязкіту на апаратному рівні застосовують пасивний інтегрувальний $RC$-фільтр із тригером Шмітта.

```
VCC (3.3V)
  |
 [R_pullup 10k]
  |
  +----+---------> До тригера Шмітта (GPIO)
  |    |
 [R_f] [C_f 100nF]
  |    |
 [SW]  GND
  |
 GND
```

Постійна часу $RC$-ланцюга $\tau$ визначає швидкість заряджання та розряджання ємності:

$$\tau = R_{\text{f}} \cdot C_{\text{f}}$$

Для повного поглинання сплесків брязкіту тривалістю $T_{\text{bounce}} \approx 5\text{ мс}$ постійна часу обирається з умови:

$$\tau \ge T_{\text{bounce}} \implies R_{\text{f}} \cdot C_{\text{f}} \ge 5\text{ мс}$$

При використанні ємності $C_{\text{f}} = 100\text{ нФ}$:

$$R_{\text{f}} \ge \frac{5 \times 10^{-3}\text{ с}}{100 \times 10^{-9}\text{ Ф}} = 50\text{ к}\Omega$$

Пологий фронт напруги, утворений $RC$-ланцюгом, пропускається через тригер Шмітта з верхнім $V_{\text{T+}}$ та нижнім $V_{\text{T-}}$ порогами перемикання (зазвичай $V_{\text{T+}} \approx 0.7 V_{CC}$, $V_{\text{T-}} \approx 0.3 V_{CC}$), що формує ідеальний прямокутний цифровий сигнал.

---

## 2. Алгоритми програмного придушення брязкіту (Debouncing)

При програмній обробці забороняється використовувати блокуючі затримки (наприклад, `delay_ms(20)`), оскільки це блокує обчислювальне ядро. Застосовують два детерміновані підходи:

### А. Алгоритм підрахунку стабільних відліків (Integrator/Counter)
Періодичний таймер викликає обробник кожні $T_{\text{sample}} = 5\text{ мс}$. Якщо зчитаний логічний рівень збігається з попереднім, лічильник збільшується. Стан вважається зміненим лише при досягненні порогу (наприклад, 4 послідовних однакових відліки = $20\text{ мс}$ стабільності).

### Б. Алгоритм зсувного регістру (Shift Register Filter)
Стан виводу зсувається у 8-бітну змінну `history`. Логічний стан "натиснуто" підтверджується лише при `history == 0x00` (для активного нуля) або `history == 0xFF` (для активної одиниці).

---

## 3. Високоефективний C/C++ Драйвер Антибрязкіту

Нижче наведено неблокуючий C/C++ модуль для одночасної обробки масиву кнопок методом періодичного зсувного регістру.

```cpp
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define DEBOUNCE_CHECK_INTERVAL_MS  5
#define BUTTON_STABLE_MASK          0xFF // 8 послідовних стабільних зчитувань

typedef struct {
    uint8_t pin_id;
    uint8_t history;          // Зсувний регістр історії відліків
    bool current_state;       // Підтверджений поточний стан (true = pressed)
    bool event_pressed;       // Прапорець події натискання (Single Edge)
    bool event_released;      // Прапорець події відпускання
} ButtonDebouncer_t;

/**
 * @brief Ініціалізація структури кнопки
 */
void button_init(ButtonDebouncer_t *btn, uint8_t pin_id) {
    btn->pin_id = pin_id;
    btn->history = 0x00; // Початковий стан: відпущено (pull-up active low)
    btn->current_state = false;
    btn->event_pressed = false;
    btn->event_released = false;
}

/**
 * @brief Периферійна функція опитування (Викликається з ISR системного таймера SysTick кожні 5 мс)
 * @param raw_pin_level Фактичний логічний рівень на виводі (0 або 1)
 */
void button_update_state(ButtonDebouncer_t *btn, bool raw_pin_level) {
    // Для схеми з Pull-Up кнопка натиснута = 0, тому інвертуємо для логіки "1 = натиснуто"
    bool sample = !raw_pin_level;

    // Зсув історії та запис нового відліку в молодший біт
    btn->history = (btn->history << 1) | (sample ? 1 : 0);

    // Перевірка на стабільний стан "Натиснуто" (всі 8 бітів = 1)
    if (btn->history == BUTTON_STABLE_MASK) {
        if (!btn->current_state) {
            btn->current_state = true;
            btn->event_pressed = true; // Спрацював фронт натискання
        }
    }
    // Перевірка на стабільний стан "Відпущено" (всі 8 бітів = 0)
    else if (btn->history == 0x00) {
        if (btn->current_state) {
            btn->current_state = false;
            btn->event_released = true; // Спрацював спад відпускання
        }
    }
}

/**
 * @brief Зчитування події натискання з автоскиданням
 */
bool button_was_pressed(ButtonDebouncer_t *btn) {
    if (btn->event_pressed) {
        btn->event_pressed = false;
        return true;
    }
    return false;
}

int main(void) {
    ButtonDebouncer_t btn1;
    button_init(&btn1, 1);

    printf("=== Симуляція Програмного Придушення Брязкіту Контактів (Debouncing) ===\n");

    // Імітація серії нестабільних відліків брязкіту при натисканні (0 = pressed, 1 = released)
    bool bounce_samples[] = { 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1 };
    size_t total_samples = sizeof(bounce_samples) / sizeof(bounce_samples[0]);

    for (size_t i = 0; i < total_samples; i++) {
        bool raw_level = bounce_samples[i];
        button_update_state(&btn1, raw_level);

        printf("Відлік %2zu | Raw Pin Level: %d | History Reg: 0x%02X | State: %s\n",
               i + 1, raw_level, btn1.history, btn1.current_state ? "PRESSED" : "RELEASED");

        if (button_was_pressed(&btn1)) {
            printf(" ---> ПОДІЯ: Зафіксовано стабільне натискання кнопки!\n");
        }
    }

    return 0;
}
```

---

## 4. Висновки

1. Механічний брязкіт контактів триває до $20\text{ мс}$ і вимагає обов'язкової фільтрації для запобігання хибним спрацьовуванням.
2. Програмний метод зсувного регістру забезпечує детерміновану затримку розпізнавання $T_{\text{delay}} = 8 \times T_{\text{sample}}$ без виклику блокуючих затримок ядра.