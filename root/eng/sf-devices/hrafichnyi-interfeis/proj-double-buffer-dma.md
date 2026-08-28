# Подвійна буферизація LVGL з неблокуючою передачею через DMA

У вбудованих графічних системах головним вузьким місцем продуктивності є передача піксельних масивів із пам'яті мікроконтролера в контролер дисплея (ST7789, ILI9341, ST7796 тощо). При роздільній здатності 320×240 пікселів із глибиною кольору 16 біт (RGB565) один повний кадр містить 153 600 байтів. На шині SPI з частотою 40 МГц блокуюча передача такого обсягу даних забирає приблизно 31 мілісекунду процесорного часу — ядро просто крутиться в порожньому циклі опитування прапорця зайнятості передавача.

Використання подвійного буфера рендерингу (англ. *double partial buffer*) у парі з контролером прямого доступу до пам'яті (DMA) та операційною системою реального часу усуває цей простій. Поки контролер DMA передає перший буфер через шину в контролер екрана, процесор паралельно прораховує пікселі наступної графічної області в другий буфер.

## Архітектурний конвеєр передачі та синхронізація

Конвеєр виведення графіки спирається на три взаємопов'язані компоненти, які утворюють замкнене кільце подій:

1. **Два буфери рендерингу в пам'яті SRAM**: Кожен буфер вміщує смугу дисплея (наприклад, 1/10 висоти екрана — 320×24 пікселі, що становить 15 360 байтів). Буфери обов'язково вирівнюються за межею 32 байти для коректної роботи з кешем даних (D-Cache) на процесорах Cortex-M7.
2. **Зворотний виклик `flush_cb`**: Викликається графічним рушієм LVGL, коли чергова область растрових даних готова. Функція встановлює апаратне вікно координат на контролері дисплея через блокуючі короткі команди, виконує скидання кешу процесора та запускає асинхронну транзакцію DMA.
3. **Обробник переривання завершення DMA (ISR)**: Після передачі останнього байта контролер DMA генерує переривання. Обробник перемикає лінію Chip Select (CS) у пасивний стан і викликає функцію `lv_disp_flush_ready()`, повідомляючи рушій про звільнення переданого буфера.

Завдяки такій схемі графічний потік (GUI Task) не витрачає час на очікування фізичної лінії передачі, а процесорний час використовується виключно для математичних розрахунків геометрії та змішування кольорів.

## Робочий приклад драйвера дисплея на C та C++

Нижче наведено повну реалізацію асинхронного драйвера дисплея з подвійним частковим буфером для мікроконтролера STM32 / ESP32 під керуванням FreeRTOS.

:::tabs
```c
#include "lvgl.h"
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "semphr.h"

#define LCD_HOR_RES     320
#define LCD_VER_RES     240
#define LCD_BUF_LINES   24    /* 1/10 висоти екрана */
#define LCD_BUF_SIZE    (LCD_HOR_RES * LCD_BUF_LINES)

/* Апаратні дескриптори периферії */
extern SPI_HandleTypeDef hspi1;
extern DMA_HandleTypeDef hdma_spi1_tx;

/* Буфери рендерингу: обов'язкове вирівнювання за 32-байтною лінією кешу */
static lv_color_t __attribute__((aligned(32))) buf1[LCD_BUF_SIZE];
static lv_color_t __attribute__((aligned(32))) buf2[LCD_BUF_SIZE];

static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t      disp_drv;

/* Семафор блокування доступу до апаратної шини SPI */
static SemaphoreHandle_t spi_mutex = NULL;

/* Допоміжні функції атомарного керування лініями дисплея */
static inline void lcd_cs_low(void)   { GPIOB->BSRR = (1 << (6 + 16)); }
static inline void lcd_cs_high(void)  { GPIOB->BSRR = (1 << 6); }
static inline void lcd_dc_cmd(void)   { GPIOB->BSRR = (1 << (7 + 16)); }
static inline void lcd_dc_data(void)  { GPIOB->BSRR = (1 << 7); }

static void lcd_send_cmd(uint8_t cmd)
{
    lcd_dc_cmd();
    lcd_cs_low();
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
    lcd_cs_high();
}

static void lcd_send_data(const uint8_t *data, uint16_t len)
{
    lcd_dc_data();
    lcd_cs_low();
    HAL_SPI_Transmit(&hspi1, (uint8_t*)data, len, HAL_MAX_DELAY);
    lcd_cs_high();
}

static void lcd_set_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    uint8_t caset[4] = { (uint8_t)(x1 >> 8), (uint8_t)(x1 & 0xFF),
                         (uint8_t)(x2 >> 8), (uint8_t)(x2 & 0xFF) };
    uint8_t raset[4] = { (uint8_t)(y1 >> 8), (uint8_t)(y1 & 0xFF),
                         (uint8_t)(y2 >> 8), (uint8_t)(y2 & 0xFF) };

    lcd_send_cmd(0x2A); /* Column Address Set: встановлення меж X */
    lcd_send_data(caset, 4);

    lcd_send_cmd(0x2B); /* Row Address Set: встановлення меж Y */
    lcd_send_data(raset, 4);

    lcd_send_cmd(0x2C); /* Memory Write: перехід у режим запису пікселів */
}

/* Зворотний виклик скидання растрового буфера в дисплей через DMA */
static void disp_flush_cb(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    uint32_t pixel_count = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);
    uint32_t byte_count  = pixel_count * sizeof(lv_color_t);

    /* Захоплюємо апаратну шину SPI перед конфігурацією вікна */
    xSemaphoreTake(spi_mutex, portMAX_DELAY);

    /* 1. Задаємо координати прямокутного вікна оновлення */
    lcd_set_window(area->x1, area->y1, area->x2, area->y2);

    /* 2. Переводимо лінію DC у режим даних і активуємо лінію CS */
    lcd_dc_data();
    lcd_cs_low();

    /* 3. Очищення кешу даних Cortex-M7 (скидання брудних рядків у фізичну SRAM) */
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    SCB_CleanDCache_by_Addr((uint32_t*)color_p, (int32_t)byte_count);
#endif

    /* 4. Запуск неблокуючої транзакції DMA */
    HAL_SPI_Transmit_DMA(&hspi1, (uint8_t*)color_p, (uint16_t)byte_count);
}

/* Обробник переривання завершення передачі DMA */
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        /* Деактивуємо вибір чипа після закінчення транзакції */
        lcd_cs_high();

        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(spi_mutex, &xHigherPriorityTaskWoken);

        /* Інформуємо графічне ядро: поточний буфер вільний для наступного рендерингу */
        lv_disp_flush_ready(&disp_drv);

        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

void gui_init(void)
{
    spi_mutex = xSemaphoreCreateMutex();

    lv_init();

    /* Реєстрація двох буферів у дескрипторі малювання */
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, LCD_BUF_SIZE);

    /* Конфігурація та реєстрація HAL-драйвера дисплея */
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res  = LCD_HOR_RES;
    disp_drv.ver_res  = LCD_VER_RES;
    disp_drv.flush_cb = disp_flush_cb;
    disp_drv.draw_buf = &draw_buf;

    lv_disp_drv_register(&disp_drv);
}

/* Фонова графічна задача FreeRTOS */
void gui_task(void *pvParameters)
{
    (void)pvParameters;
    gui_init();

    TickType_t last_wake = xTaskGetTickCount();
    while (1) {
        /* Обробка черги таймерів, анімацій та виклик рендерингу */
        lv_timer_handler();
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(5));
    }
}
```
```cpp
#include "lvgl.h"
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "semphr.h"
#include <span>
#include <memory>
#include <concepts>

extern SPI_HandleTypeDef hspi1;

namespace embedded::gui {

template <size_t Width, size_t Height, size_t LinesPerBuffer>
class DisplayDriver {
public:
    static constexpr size_t kWidth          = Width;
    static constexpr size_t kHeight         = Height;
    static constexpr size_t kBufferSize     = Width * LinesPerBuffer;
    static constexpr size_t kBufferBytes    = kBufferSize * sizeof(lv_color_t);

    explicit DisplayDriver(SPI_HandleTypeDef& spi) noexcept : spi_(spi)
    {
        instance_ = this;
        spi_mutex_ = xSemaphoreCreateMutex();
    }

    ~DisplayDriver() noexcept
    {
        if (spi_mutex_ != nullptr) {
            vSemaphoreDelete(spi_mutex_);
        }
        if (instance_ == this) {
            instance_ = nullptr;
        }
    }

    DisplayDriver(const DisplayDriver&) = delete;
    DisplayDriver& operator=(const DisplayDriver&) = delete;

    void init() noexcept
    {
        lv_init();

        lv_disp_draw_buf_init(&draw_buf_, buffer1_, buffer2_, kBufferSize);

        lv_disp_drv_init(&disp_drv_);
        disp_drv_.hor_res   = static_cast<lv_coord_t>(kWidth);
        disp_drv_.ver_res   = static_cast<lv_coord_t>(kHeight);
        disp_drv_.flush_cb  = &DisplayDriver::flushTrampoline;
        disp_drv_.draw_buf  = &draw_buf_;
        disp_drv_.user_data = this;

        lv_disp_drv_register(&disp_drv_);
    }

    void onDmaTransferComplete() noexcept
    {
        csHigh();

        BaseType_t higherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(spi_mutex_, &higherPriorityTaskWoken);

        lv_disp_flush_ready(&disp_drv_);

        portYIELD_FROM_ISR(higherPriorityTaskWoken);
    }

    static DisplayDriver* getInstance() noexcept { return instance_; }

private:
    static inline DisplayDriver* instance_{nullptr};

    SPI_HandleTypeDef&  spi_;
    SemaphoreHandle_t   spi_mutex_{nullptr};

    alignas(32) lv_color_t buffer1_[kBufferSize]{};
    alignas(32) lv_color_t buffer2_[kBufferSize]{};

    lv_disp_draw_buf_t  draw_buf_{};
    lv_disp_drv_t       disp_drv_{};

    static void csLow()    noexcept { GPIOB->BSRR = (1 << (6 + 16)); }
    static void csHigh()   noexcept { GPIOB->BSRR = (1 << 6); }
    static void dcCmd()    noexcept { GPIOB->BSRR = (1 << (7 + 16)); }
    static void dcData()   noexcept { GPIOB->BSRR = (1 << 7); }

    void sendCommand(uint8_t cmd) noexcept
    {
        dcCmd();
        csLow();
        HAL_SPI_Transmit(&spi_, &cmd, 1, HAL_MAX_DELAY);
        csHigh();
    }

    void sendData(std::span<const uint8_t> data) noexcept
    {
        dcData();
        csLow();
        HAL_SPI_Transmit(&spi_, const_cast<uint8_t*>(data.data()), 
                         static_cast<uint16_t>(data.size()), HAL_MAX_DELAY);
        csHigh();
    }

    void setWindow(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2) noexcept
    {
        const uint8_t caset[4] = {
            static_cast<uint8_t>(x1 >> 8), static_cast<uint8_t>(x1 & 0xFF),
            static_cast<uint8_t>(x2 >> 8), static_cast<uint8_t>(x2 & 0xFF)
        };
        const uint8_t raset[4] = {
            static_cast<uint8_t>(y1 >> 8), static_cast<uint8_t>(y1 & 0xFF),
            static_cast<uint8_t>(y2 >> 8), static_cast<uint8_t>(y2 & 0xFF)
        };

        sendCommand(0x2A);
        sendData(caset);

        sendCommand(0x2B);
        sendData(raset);

        sendCommand(0x2C);
    }

    static void flushTrampoline(lv_disp_drv_t* drv, const lv_area_t* area, lv_color_t* color_p)
    {
        auto* self = static_cast<DisplayDriver*>(drv->user_data);
        self->flush(area, color_p);
    }

    void flush(const lv_area_t* area, lv_color_t* color_p) noexcept
    {
        const size_t pixels = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);
        const size_t bytes  = pixels * sizeof(lv_color_t);

        xSemaphoreTake(spi_mutex_, portMAX_DELAY);

        setWindow(static_cast<uint16_t>(area->x1), static_cast<uint16_t>(area->y1),
                  static_cast<uint16_t>(area->x2), static_cast<uint16_t>(area->y2));

        dcData();
        csLow();

#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
        SCB_CleanDCache_by_Addr(reinterpret_cast<uint32_t*>(color_p), static_cast<int32_t>(bytes));
#endif

        HAL_SPI_Transmit_DMA(&spi_, reinterpret_cast<uint8_t*>(color_p), 
                             static_cast<uint16_t>(bytes));
    }
};

} // namespace embedded::gui

/* Обробник переривання HAL із викликом екземпляра класу */
extern "C" void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        auto* driver = embedded::gui::DisplayDriver<320, 240, 24>::getInstance();
        if (driver != nullptr) {
            driver->onDmaTransferComplete();
        }
    }
}
```
:::

## Детальний розбір механізмів та прихованих пасток

При побудові асинхронного драйвера дисплея з подвійною буферизацією виникає низка специфічних апаратних і системних конфліктів, які не проявляються в простих синхронних прикладах.

### 1. Межа лічильника передач DMA (NDTR)

У більшості мікроконтролерів (зокрема STM32 серій F4/F7/G4) регістр кількості елементів передачі DMA (`DMA_SxNDTR`) є 16-розрядним. Це означає, що за одну транзакцію контролер може переслати щонайбільше 65 535 одиниць даних (байт або півслів).

Якщо буфер рендерингу перевищує 64 КБ (наприклад, при роздільній здатності 800×480 пікселів смуга на 1/10 екрана займає 800×48×2 = 76 800 байтів):
- Спроба передати цей масив як послідовність байтів з параметром `DataSize = DMA_PDATAALIGN_BYTE` призведе до переповнення регістра `NDTR` і спотворення передачі (буде передано лише `76800 % 65536 = 11264` байти).
- Вирішенням є конфігурація каналу DMA на передачу 16-бітних слів (`DMA_PDATAALIGN_HALFWORD` / `DMA_MDATAALIGN_HALFWORD`). У такому разі лічильник `NDTR` містить кількість пікселів (38 400), що чудово вкладається у 16-бітний діапазон.

### 2. Когерентність кешу даних L1 D-Cache

На мікроконтролерах із ядрами Cortex-M7 (STM32F7, STM32H7) та Cortex-M33 кеш даних працює за алгоритмом відкладеного запису (**Write-Back**). Коли процесор обчислює значення пікселів у буфері `buf1`, змінені байти накопичуються в кеш-пам'яті першого рівня і не одразу потрапляють у фізичну пам'ять SRAM.

Контролер DMA є периферійним майстром шини (Bus Master) і звертається безпосередньо до фізичної пам'яті SRAM, оминаючи процесорний кеш. Якщо перед запуском передачі не виконати операцію примусового скидання кешу (`Clean`):
- DMA прочитає старі або сміттєві дані зі статичної пам'яті.
- На екрані з'являться горизонтальні смуги зі спотвореними кольорами або фрагменти старих кадрів.
- Очищення кешу здійснюється функцією `SCB_CleanDCache_by_Addr()`, яка скидає всі брудні рядки кешу, що перетинаються з адресами буфера.

Крім того, оскільки один рядок кешу Cortex-M7 займає рівно 32 байти, розмір та адреса початку кожного буфера мають бути кратними 32 байтам. В іншому випадку скидання сусідніх рядків кешу іншими задачами може затерти дані графічного буфера.

### 3. Розділення шини SPI між дисплеєм і сенсорним контролером

У компактних пристроях дисплей та сенсорний контролер (тачскрін) часто підключають до однієї спільної шини SPI. Це створює серйозний ризик апаратного конфлікту:
- Поки DMA передає 15 КБ пікселів на дисплей з опущеною лінією `LCD_CS`, задача опитування сенсора може спробувати передати команду опитування координат тачскріна з опущеною лінією `TOUCH_CS`.
- На лініях MISO/MOSI виникне колізія сигналів, а обидва периферійні чипи отримають спотворені пакети.

Для уникнення цього конфлікту доступ до шини захищається м'ютексом RTOS (`spi_mutex`). Функція `flush_cb` захоплює м'ютекс перед стартом DMA і опускає `LCD_CS`. Підняття `LCD_CS` у високий стан і звільнення м'ютексу здійснюються строго всередині обробника переривання завершення DMA (`HAL_SPI_TxCpltCallback`). Будь-яка інша задача, що намагається використати SPI, буде заблокована на м'ютексі до завершення передачі поточної графічної смуги.
