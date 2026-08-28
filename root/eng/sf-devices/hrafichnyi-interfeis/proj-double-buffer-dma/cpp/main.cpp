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
