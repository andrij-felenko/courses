#include "rig.h"

#include <stdatomic.h>

#include "hw.h"
#include "stm32f4xx.h"

// Стан ділять обробник переривання й головний цикл. Прапорці атомарні:
// без цього компілятор має право переставити запис результату після запису
// «результат готовий», і головний цикл забере попереднє значення.
static atomic_uint  g_state      = ATOMIC_VAR_INIT(RIG_IDLE);
static atomic_uint  g_start_us   = ATOMIC_VAR_INIT(0);
static atomic_uint  g_capture_us = ATOMIC_VAR_INIT(0);
static atomic_bool  g_ready      = ATOMIC_VAR_INIT(false);

void EXTI0_IRQHandler(void)
{
    // Найперший рядок обробника — зняття часу. Усе інше вже не впливає на вимір.
    const uint32_t now = hw_now_us();

    EXTI->PR = EXTI_PR_PR0;

    if (atomic_load_explicit(&g_state, memory_order_relaxed) != RIG_WAITING) {
        return; // спрацювання поза вікном виміру: шум, дзвін фронту, відлуння
    }

    hw_led(false);
    hw_optical_window(false); // одне випробування — один фронт

    const uint32_t start = atomic_load_explicit(&g_start_us, memory_order_relaxed);
    atomic_store_explicit(&g_capture_us, now - start, memory_order_relaxed);
    atomic_store_explicit(&g_state, RIG_COOLDOWN, memory_order_relaxed);
    // Releaseом закриваємо запис: усе вище стає видимим до прапорця готовності.
    atomic_store_explicit(&g_ready, true, memory_order_release);
}

void rig_init(void)
{
    hw_optical_window(false);
    hw_led(false);
    atomic_store_explicit(&g_ready, false, memory_order_relaxed);
    atomic_store_explicit(&g_state, RIG_IDLE, memory_order_relaxed);
}

bool rig_trigger(void)
{
    if (atomic_load_explicit(&g_state, memory_order_relaxed) != RIG_IDLE) {
        return false;
    }

    atomic_store_explicit(&g_ready, false, memory_order_relaxed);
    atomic_store_explicit(&g_state, RIG_WAITING, memory_order_relaxed);

    // Порядок принциповий: вікно чутливості відкриваємо ДО спалаху, інакше
    // на дуже коротких трактах фронт відгуку встиг би прийти в замасковане
    // переривання й пропав би. Мітку часу знімаємо впритул до запалювання —
    // між записом у BSRR і читанням CNT лежить один такт шини.
    hw_optical_window(true);
    hw_led(true);
    atomic_store_explicit(&g_start_us, hw_now_us(), memory_order_relaxed);
    return true;
}

rig_result_t rig_poll(void)
{
    rig_result_t result = { .completed = false, .timed_out = false, .latency_us = 0u };

    if (atomic_load_explicit(&g_ready, memory_order_acquire)) {
        atomic_store_explicit(&g_ready, false, memory_order_relaxed);
        result.completed  = true;
        result.latency_us = atomic_load_explicit(&g_capture_us, memory_order_relaxed);
        return result;
    }

    if (atomic_load_explicit(&g_state, memory_order_relaxed) == RIG_WAITING) {
        const uint32_t start = atomic_load_explicit(&g_start_us, memory_order_relaxed);
        if ((hw_now_us() - start) >= RIG_TIMEOUT_US) {
            // Гасимо світло й закриваємо вікно ДО зміни стану: інакше фронт,
            // що прийшов би саме зараз, ще застав би RIG_WAITING і додав
            // фальшивий зразок поверх уже зарахованого таймауту.
            hw_led(false);
            hw_optical_window(false);
            atomic_store_explicit(&g_state, RIG_COOLDOWN, memory_order_relaxed);
            atomic_store_explicit(&g_ready, false, memory_order_relaxed);

            result.completed  = true;
            result.timed_out  = true;
            result.latency_us = RIG_TIMEOUT_US;
        }
    }

    return result;
}

void rig_arm(void)
{
    if (atomic_load_explicit(&g_state, memory_order_relaxed) == RIG_COOLDOWN) {
        atomic_store_explicit(&g_state, RIG_IDLE, memory_order_relaxed);
    }
}

rig_state_t rig_state(void)
{
    return (rig_state_t)atomic_load_explicit(&g_state, memory_order_relaxed);
}
