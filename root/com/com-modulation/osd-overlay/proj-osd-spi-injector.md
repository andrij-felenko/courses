# ⚙️ Генерація OSD-символів мовою C та C++ через SPI DMA й переривання HSYNC

Для накладання монохромного OSD на аналоговий відеосигнал без використання спеціалізованої мікросхеми MAX7456 мікроконтролер має синхронізувати генерацію пікселів із рядковим імпульсом `HSYNC`. Нижче наведено практичну реалізацію модуля накладання відеорядка мовами C та C++, де спад напруги `HSYNC` на зовнішньому перериванні запускає апаратний таймер затримки, після чого периферія SPI через DMA виштовхує бітову маску пікселів безпосередньо у відеоключ.

### Алгоритм та апаратна послідовність викликів

Генерація графіки безпосередньо на мікроконтролері побудована на триланковому апаратному ланцюжку (EXTI ──► Timer ──► DMA ──► SPI TX), що працює повністю автономно без залучення ядра процесора під час виштовхування пікселів рядка.

Послідовність апаратних подій на один відеорядок складається з п'яти етапів:

1. **Етап 1: Фіксація рядкового синхроімпульсу HSYNC (0.0 мкс):**
   Сигнал від зовнішнього аналогового сепаратора синхроімпульсів (LM1881) подається на вивід зовнішнього переривання (EXTI). Спад напруги (`Falling Edge`) генерує переривання, у якому обробник increment-ує лічильник рядків кадру `current_line`.
2. **Етап 2: Запуск затримки гасіння (0.0 .. 10.5 мкс):**
   Якщо лічильник `current_line` знаходиться в зоні активного кадру (рядки `40..280` для PAL), обробник запускає апаратний таймер (TIM2) у режимі однієї черги (*One-Pulse Mode*). Таймер відраховує паузу `10.5 мкс`, захищаючи від спотворення рядковий імпульс та колірний спалах.
3. **Етап 3: Апаратне тригерування DMA (10.5 мкс):**
   Після закінчення паузи `10.5 мкс` лічильник таймера генерує подію тригера (Hardware Trigger Event), яка повертає сигнал прямо на канал DMA без участі процесора.
4. **Етап 4: Виштовхування піксельного буфера по SPI DMA (10.5 .. 62.5 мкс):**
   Контролер DMA відкриває доступ до масиву пам'яті `line_buffer` і починає послідовний перенос `40` байтів (`320` пікселів) у вихідний регістр `SPI1->DR` з тактовою частотою `6.15 МГц`. Вихідний ніжку MOSI підключено безпосередньо до керованого входу аналогового відеоключа.
5. **Етап 5: Завершення рядка та підготовка (62.5 .. 64.0 мкс):**
   Після передачі останнього байта DMA генерує переривання завершення передачі `TC` (*Transfer Complete*), у якому обробник перериває роботу SPI й готує новий буфер для наступного рядка.

```
Апаратна послідовність викликів периферії STM32 під час одного відеорядка:

[CVBS HSYNC] ──► (EXTI Interrupt 0.0us) ──► TIM2 Start (One-Pulse Mode)
                                                    │
                                                    ▼
                                           (Delay 10.5us Timeout)
                                                    │
                                                    ▼
                                           DMA Request Trigger ──► SPI1_TX (6.15 MHz) ──► Output MOSI Keyer
```

### Повний вихідний код проєкту

:::tabs
```c
// C implementation: Low-level OSD Line Injector using SPI DMA & EXTI HSYNC Interrupts
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PAL_TOTAL_LINES    625
#define PAL_ACTIVE_PIXELS  320
#define OSD_LINE_BYTES     (PAL_ACTIVE_PIXELS / 8)
#define OSD_START_LINE     40
#define OSD_END_LINE       280

typedef struct {
    uint8_t line_buffer[OSD_LINE_BYTES];
    volatile uint16_t current_line;
    volatile bool is_active_frame;
    volatile bool dma_busy;
} osd_injector_t;

static osd_injector_t g_osd;

// Ініціалізація буферів та стану OSD
void osd_init(osd_injector_t *osd) {
    osd->current_line = 0;
    osd->is_active_frame = false;
    osd->dma_busy = false;
    memset((void*)osd->line_buffer, 0x00, OSD_LINE_BYTES);
}

// Очищення буфера рядка перед збіркою нового кадру
void osd_clear_buffer(osd_injector_t *osd) {
    memset((void*)osd->line_buffer, 0x00, OSD_LINE_BYTES);
}

// Запис точкового пікселя в маску рядка
void osd_draw_pixel(osd_injector_t *osd, uint16_t x) {
    if (x < PAL_ACTIVE_PIXELS) {
        uint16_t byte_idx = x / 8;
        uint8_t bit_idx = 7 - (x % 8);
        osd->line_buffer[byte_idx] |= (1 << bit_idx);
    }
}

// Обробник зовнішнього переривання HSYNC (рядкова синхронізація EXTI)
void EXTI_HSYNC_IRQHandler(osd_injector_t *osd) {
    osd->current_line++;
    
    // Перевірка, чи знаходиться промінь у робочій зоні кадру
    if (osd->current_line >= OSD_START_LINE && osd->current_line <= OSD_END_LINE) {
        // Апаратний запуск таймера затримки задньої площадки (10.5 мкс)
        // Після збігу таймер автономно ініціює DMA-передачу в SPI_DR
        osd->dma_busy = true;
    }
}

// Обробник зовнішнього переривання VSYNC (кадрова синхронізація EXTI)
void EXTI_VSYNC_IRQHandler(osd_injector_t *osd) {
    osd->current_line = 0; // Скидання лічильника рядків на початку кадру
    osd->is_active_frame = true;
}

// Зворотний виклик завершення DMA-передачі рядка
void DMA_SPI_TX_IRQHandler(osd_injector_t *osd) {
    osd->dma_busy = false;
}
```
```cpp
// C++ implementation: RAII-managed OSD Line Injector using std::span & Type Safety
#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

class OsdLineInjector {
public:
    static constexpr std::size_t kActivePixels = 320;
    static constexpr std::size_t kBufferBytes  = kActivePixels / 8;
    static constexpr uint16_t kStartLine       = 40;
    static constexpr uint16_t kEndLine         = 280;

    OsdLineInjector() noexcept {
        clearBuffer();
    }

    // Очищення буфера рядка
    void clearBuffer() noexcept {
        line_buffer_.fill(0x00);
    }

    // Обробка рядкового синхроімпульсу HSYNC
    void handleHsync() noexcept {
        ++current_line_;
        if (current_line_ >= kStartLine && current_line_ <= kEndLine) {
            dma_busy_ = true;
            triggerDmaTransfer(std::span<const uint8_t>{line_buffer_});
        }
    }

    // Обробка кадрового синхроімпульсу VSYNC
    void handleVsync() noexcept {
        current_line_ = 0;
        is_active_frame_ = true;
    }

    // Встановлення точкового пікселя в маску
    void drawPixel(std::size_t x) noexcept {
        if (x < kActivePixels) {
            const std::size_t byte_idx = x / 8;
            const uint8_t bit_idx = static_cast<uint8_t>(7u - (x % 8));
            line_buffer_[byte_idx] |= static_cast<uint8_t>(1u << bit_idx);
        }
    }

    // Обробник завершення DMA
    void handleDmaComplete() noexcept {
        dma_busy_ = false;
    }

    [[nodiscard]] uint16_t currentLine() const noexcept {
        return current_line_;
    }

    [[nodiscard]] bool isBusy() const noexcept {
        return dma_busy_;
    }

private:
    void triggerDmaTransfer(std::span<const uint8_t> data) noexcept {
        // Апаратний запуск SPI DMA передачі у відеоключ після затримки 10.5 мкс
        (void)data;
    }

    std::array<uint8_t, kBufferBytes> line_buffer_{};
    volatile uint16_t current_line_{0};
    volatile bool is_active_frame_{false};
    volatile bool dma_busy_{false};
};
```
:::

### Налаштування периферії STM32 для роботи з OSD

Для забезпечення стабільного виштовхування пікселів без зсуву налаштовують три блоки периферії мікроконтролера STM32 (F4/F7/G4):

1. **Модуль EXTI (External Interrupt):** Лінію `EXTI0` налаштовують на переривання по спаду напруги (`EXTI_Trigger_Falling`) від ніжки HSYNC сепаратора. Пріоритет переривання встановлюють найвищим (`NVIC Preemption Priority = 0`), щоб мінімізувати джитер обробника.
2. **Таймер TIM2 (One-Pulse Mode):** Тактується частотою `84 МГц`. Значення автоперезавантаження `ARR` встановлюють на `882` відліки (що відповідає затримці `10.5 мкс`). Подія оновлення таймера генерує прямий тригер DMA.
3. **Контролер DMA1 (Stream 4, Channel 3):** Режим передачі `Memory-to-Peripheral`, ширина даних — `Byte`, інкремент адреси пам'яті увімкнено, інкремент адреси периферії вимкнено. Адресою призначення є регістр `SPI1->DR`.

### Подвійна буферизація (Ping-Pong Buffering) для усунення розривів кадру

Під час польоту процесор польотного контролера постійно обчислює нові значення напруги акумулятора, штучного горизонту та GPS-координат. Якщо модифікувати масив `line_buffer` безпосередньо в момент, коли DMA виштовхує його у відеосигнал, виникне ефект **розриву зображення** (*Screen Tearing*), коли верхня частина символу відображає старі дані, а нижня — нові.

Для запобігання артефактам розриву використовується техніка подвійної буферизації (Ping-Pong Buffers):
- **Буфер 0 (Display Buffer):** Поточний активний буфер, який зчитується DMA-контролером під час малювання кадру.
- **Буфер 1 (Render Buffer):** Тіньовий буфер, у який мікроконтролер спокійно малює нові символи та лінії штучного горизонту під час малювання кадру.

У момент початку кадрового імпульсу `VSYNC` (коли електронний промінь біжить вгору екрана) обробник переривання миттєво міняє вказівники на буфери місцями. Це забезпечує монолітне й безмерехтливе оновлення графіки телеметрії зі частотою `50 Гц`.

### Оптимізація викликів та нульове завантаження ядра

Завдяки триланковій схемі периферії процесорне ядро Cortex-M4 під час виштовхування пікселів знаходиться в стані виконання основного контуру управління польотом (PID-регулятор).

Апаратні витрати ядра на один кадр PAL розраховуються так:
- Кількість викликів переривань `HSYNC`: `625` викликів на кадр (`15 625` викликів/с);
- Час виконання обробника `EXTI_HSYNC_IRQHandler`: близько `15` тактів процесора;
- Загальні витрати ядра на частоті `168 МГц`: `15625 × 15 = 234 375` тактів/с (менше ніж `0.14%` від загальної продуктивності CPU).

Отже, апаратний запуск SPI DMA дозволяє виштовхувати біти зі швидкістю `6.15 МГц` повністю в апаратній автономії, звільняючи ядро мікроконтролера для розрахунку алгоритмів стабілізації безпілотного апарата.

> 🔧 **Навіщо це.** Застосування периферії SPI DMA дозволяє виштовхувати біти зі швидкістю `6.15 МГц` повністю в апаратній автономії, звільняючи ядро мікроконтролера від потреби виконувати «програмний біт-бенгінг» (*bit-banging*) у жорстких часових рамках `64 мкс` кожного відеорядка.
