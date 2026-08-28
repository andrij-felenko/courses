/* platform_timer_shim.c — Ізольований C-адаптер для запобігання правкам у ядрі */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Імітація внутрішнього API ядра версії v1 проти v2 */
#if defined(USE_KERNEL_API_V2)
typedef struct {
    void *mmio_base;
    uint32_t freq_hz;
    uint32_t irq_priority;
} kernel_timer_raw_t;

int kernel_raw_timer_start(kernel_timer_raw_t *t, uint32_t freq_hz);
void kernel_raw_timer_stop(kernel_timer_raw_t *t);
#else
typedef struct {
    uint32_t register_base;
    uint16_t clock_mhz;
} kernel_timer_raw_t;

int kernel_raw_timer_init(kernel_timer_raw_t *t, uint16_t mhz);
void kernel_raw_timer_disable(kernel_timer_raw_t *t);
#endif

/* Публічний контракт, який бачить прикладний код продукту */
typedef struct {
    kernel_timer_raw_t native_handle;
    uint32_t configured_freq_hz;
    bool is_running;
} product_timer_handle_t;

int product_timer_init(product_timer_handle_t *timer, uint32_t target_freq_hz) {
    if (!timer || target_freq_hz == 0) {
        return -1;
    }

    timer->configured_freq_hz = target_freq_hz;
    int status = 0;

#if defined(USE_KERNEL_API_V2)
    /* Адаптація під інтерфейс нового ядра v2 */
    timer->native_handle.freq_hz = target_freq_hz;
    timer->native_handle.irq_priority = 2;
    status = kernel_raw_timer_start(&timer->native_handle, target_freq_hz);
#else
    /* Підтримка застарілого інтерфейсу ядра v1 */
    uint16_t mhz = (uint16_t)(target_freq_hz / 1000000UL);
    status = kernel_raw_timer_init(&timer->native_handle, mhz);
#endif

    if (status == 0) {
        timer->is_running = true;
    }
    return status;
}

void product_timer_shutdown(product_timer_handle_t *timer) {
    if (!timer || !timer->is_running) {
        return;
    }

#if defined(USE_KERNEL_API_V2)
    kernel_raw_timer_stop(&timer->native_handle);
#else
    kernel_raw_timer_disable(&timer->native_handle);
#endif

    timer->is_running = false;
}
