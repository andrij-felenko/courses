# Порівняльний Аналіз Апаратних та Програмних FIFO у Мікроконтролерах

При розробці високоефективних вбудованих систем вибір між **апаратними буферами FIFO (Hardware FIFO)**, вбудованими у периферійні контролери (UART, SPI, CAN, USB), та **програмними FIFO (Software Ring Buffers)**, у оперативній пам'яті (SRAM), є визначальним фактором для продуктивності процесора та стабільності зв'язку.

Цей документ розглядає архітектурні відмінності, математичний аналіз завантаження ЦПУ та приклад програмної конфігурації апаратних FIFO у мікроконтролерах.

---

## 1. Архітектурні відмінності

### Апаратний FIFO (Hardware FIFO)
Апаратний FIFO — це набір внутрішніх регістрів або спеціалізованої двопортової пам'яті (SRAM Block), інтегрованої безпосередньо у периферійний модуль (наприклад, UART контролер).
- **Плюси**: Нульове залучення ядра ЦПУ при прийомі даних, автоматичне керування апаратними порогами (Watermarks) та потоком (RTS/CTS Hardware Flow Control).
- **Мінуси**: Фіксований та обмежений розмір (наприклад, 8–16 байт у STM32 USART чи 128 байт у ESP32 UART).

### Програмний FIFO (Software FIFO)
Програмний FIFO — це кільцевий буфер у системній оперативній пам'яті (SRAM), який контролюється програмно через індекси `head` та `tail`.
- **Плюси**: Гнучкий та практично необмежений розмір (від десятків байт до мегабайт).
- **Мінуси**: Вимагає обробки переривань ЦПУ або каналу DMA на кожен байт/блок, що створює накладні витрати на перемикання контексту.

```
[ Зовнішня лінія ] ---> [ Hardware FIFO (128 bytes) ] --(Watermark ISR / DMA)--> [ Software FIFO (4096 bytes in SRAM) ] ---> [ App Task ]
```

---

## 2. Математична модель частоти переривань та навантаження ЦПУ

Нехай швидкість передачі даних по шині UART становить $B$ бод (біт/с). Кожен кадр даних містить 1 стартовий біт, 8 біт даних та 1 стоповий біт (разом $10\text{ біт/байт}$). Потік байтів за секунду:

$$R_{\text{byte}} = \frac{B}{10} \quad [\text{байт/с}]$$

### Випадок 1: Без апаратного FIFO (Побайтове переривання)
Переривання викликається на кожен прийнятий байт. Частота переривань $f_{\text{isr1}}$:

$$f_{\text{isr1}} = R_{\text{byte}} = \frac{B}{10} \quad [\text{Гц}]$$

Якщо час обробки одного переривання (збереження контексту, виклик ISR, читання регістру `DR`, відновлення контексту) становить $T_{\text{isr}}$ секунд, завантаження ЦПУ $\text{CPU}_{\text{load}}$ становить:

$$\text{CPU}_{\text{load1}} = f_{\text{isr1}} \cdot T_{\text{isr}} = \frac{B}{10} \cdot T_{\text{isr}}$$

### Випадок 2: З апаратним FIFO (Поріг Watermark = $W$ байт)
Переривання викликається лише тоді, коли апаратний FIFO заповнився до рівня $W$ (Watermark Level) або виник таймаут простою лінії (IDLE Line / RX Timeout). Частота переривань:

$$f_{\text{isr2}} = \frac{R_{\text{byte}}}{W} = \frac{B}{10 \cdot W} \quad [\text{Гц}]$$

Завантаження ЦПУ зменшується пропорційно розміру порогу $W$:

$$\text{CPU}_{\text{load2}} = \frac{\text{CPU}_{\text{load1}}}{W}$$

### Числовий приклад
Для $B = 921\,600\text{ бод}$ ($R_{\text{byte}} = 92\,160\text{ байт/с}$), при $T_{\text{isr}} = 2\text{ мкс}$:
- **Без FIFO**: $f_{\text{isr}} = 92\,160\text{ Гц} \implies \text{CPU}_{\text{load}} = 92\,160 \times 2 \times 10^{-6} = 18.4\%$.
- **З апаратним FIFO ($W = 128$ байт в ESP32)**: $f_{\text{isr}} = \frac{92160}{128} = 720\text{ Гц} \implies \text{CPU}_{\text{load}} = 720 \times 2 \times 10^{-6} = 0.14\%$.

Використання апаратного FIFO знижує навантаження процесора в **128 разів**!

---

## 3. Практичний драйвер конфігурації Апаратного FIFO на C/C++

Нижче наведено бібліотечний модуль C/C++ для розрахунку параметрів завантаження ЦПУ та апаратної конфігурації порогів Hardware FIFO.

```cpp
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Конфігурація порогів апаратного FIFO
typedef enum {
    HW_FIFO_WATERMARK_1_8  = 1, // 1/8 від об'єму
    HW_FIFO_WATERMARK_1_4  = 2, // 1/4 від об'єму
    HW_FIFO_WATERMARK_1_2  = 4, // 1/2 від об'єму
    HW_FIFO_WATERMARK_3_4  = 6, // 3/4 від об'єму
    HW_FIFO_WATERMARK_FULL = 8  // Майже повний
} HwFifoWatermark_t;

typedef struct {
    uint32_t fifo_total_size_bytes; // Загальний розмір апаратного FIFO
    uint32_t baud_rate;             // Швидкість у бодах
    uint32_t watermark_bytes;       // Поріг спрацювання переривання
    double calculated_isr_freq_hz;  // Розрахована частота переривань
    double cpu_load_percent;        // Оцінка завантаження ЦПУ
} HwFifoConfig_t;

/**
 * @brief Розрахунок аналітики продуктивності для Hardware FIFO
 */
void calculate_hw_fifo_performance(HwFifoConfig_t *cfg, double isr_execution_time_sec) {
    if (!cfg || cfg->baud_rate == 0 || cfg->watermark_bytes == 0) return;

    double bytes_per_sec = (double)cfg->baud_rate / 10.0;
    cfg->calculated_isr_freq_hz = bytes_per_sec / (double)cfg->watermark_bytes;
    cfg->cpu_load_percent = (cfg->calculated_isr_freq_hz * isr_execution_time_sec) * 100.0;
}

int main(void) {
    printf("=== Порівняльний Аналіз Апаратних та Програмних FIFO ===\n\n");

    uint32_t baud_rates[] = { 115200, 460800, 921600, 3000000 };
    double isr_time_sec = 1.5e-6; // 1.5 мікросекунди на ISR

    for (int i = 0; i < 4; i++) {
        uint32_t baud = baud_rates[i];
        printf("--- Розрахунок для швидкості UART: %u baud ---\n", baud);

        // Без FIFO (1 байт)
        HwFifoConfig_t cfg_no_fifo = { .fifo_total_size_bytes = 1, .baud_rate = baud, .watermark_bytes = 1 };
        calculate_hw_fifo_performance(&cfg_no_fifo, isr_time_sec);

        // Малий апаратний FIFO (STM32 USART 8 байт, watermark 4 байти)
        HwFifoConfig_t cfg_stm32 = { .fifo_total_size_bytes = 8, .baud_rate = baud, .watermark_bytes = 4 };
        calculate_hw_fifo_performance(&cfg_stm32, isr_time_sec);

        // Великий апаратний FIFO (ESP32 128 байт, watermark 112 байт)
        HwFifoConfig_t cfg_esp32 = { .fifo_total_size_bytes = 128, .baud_rate = baud, .watermark_bytes = 112 };
        calculate_hw_fifo_performance(&cfg_esp32, isr_time_sec);

        printf(" 1) Без FIFO (1 B):    Частота ISR = %8.1f Гц | CPU Load = %6.2f %%\n",
               cfg_no_fifo.calculated_isr_freq_hz, cfg_no_fifo.cpu_load_percent);
        printf(" 2) STM32 (4 B WM):    Частота ISR = %8.1f Гц | CPU Load = %6.2f %%\n",
               cfg_stm32.calculated_isr_freq_hz, cfg_stm32.cpu_load_percent);
        printf(" 3) ESP32 (112 B WM):  Частота ISR = %8.1f Гц | CPU Load = %6.2f %%\n\n",
               cfg_esp32.calculated_isr_freq_hz, cfg_esp32.cpu_load_percent);
    }

    return 0;
}
```

---

## 4. Висновки

1. **Апаратний FIFO** є обов'язковим першим рубежем прийому високошвидкісних потоків даних ($>115200\text{ бод}$) для мінімізації частоти переривань.
2. **Програмний FIFO** слугує містком другого рівня у системній SRAM для накопичення пакетів даних великого об'єму між викликами фонових задач RTOS.
3. Оптимальною архітектурою є зв'язка **Hardware FIFO (Watermark + RX Timeout) $\rightarrow$ DMA Transfer $\rightarrow$ Software Ring Buffer**.
