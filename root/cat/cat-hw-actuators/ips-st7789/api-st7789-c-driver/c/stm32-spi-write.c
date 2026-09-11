/* Прив'язка HAL ST7789 до платформи STM32 на базі STM32Cube HAL */
#include "stm32f4xx_hal.h"

typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef      *cs_port;
    uint16_t           cs_pin;
    GPIO_TypeDef      *dc_port;
    uint16_t           dc_pin;
    GPIO_TypeDef      *rst_port;
    uint16_t           rst_pin;
    GPIO_TypeDef      *blk_port;
    uint16_t           blk_pin;
} stm32_display_ctx_t;

static void stm32_spi_write(const uint8_t *data, size_t len, void *user_data) {
    stm32_display_ctx_t *ctx = (stm32_display_ctx_t *)user_data;
    HAL_SPI_Transmit(ctx->hspi, (uint8_t *)data, (uint16_t)len, HAL_MAX_DELAY);
}

static void stm32_set_cs(uint8_t level, void *user_data) {
    stm32_display_ctx_t *ctx = (stm32_display_ctx_t *)user_data;
    HAL_GPIO_WritePin(ctx->cs_port, ctx->cs_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void stm32_set_dc(uint8_t level, void *user_data) {
    stm32_display_ctx_t *ctx = (stm32_display_ctx_t *)user_data;
    HAL_GPIO_WritePin(ctx->dc_port, ctx->dc_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void stm32_set_rst(uint8_t level, void *user_data) {
    stm32_display_ctx_t *ctx = (stm32_display_ctx_t *)user_data;
    HAL_GPIO_WritePin(ctx->rst_port, ctx->rst_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void stm32_set_blk(uint8_t level, void *user_data) {
    stm32_display_ctx_t *ctx = (stm32_display_ctx_t *)user_data;
    HAL_GPIO_WritePin(ctx->blk_port, ctx->blk_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

void st7789_bind_stm32(st7789_t *dev, stm32_display_ctx_t *ctx) {
    dev->spi_write = stm32_spi_write;
    dev->set_cs    = stm32_set_cs;
    dev->set_dc    = stm32_set_dc;
    dev->set_rst   = stm32_set_rst;
    dev->set_blk   = stm32_set_blk;
    dev->delay_ms  = HAL_Delay;
    dev->user_data = ctx;
}
