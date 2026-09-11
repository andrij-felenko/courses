#include "xpt8871.h"

/* Допоміжні функції кільцевого буфера SPSC (Single Producer, Single Consumer) */

static inline bool buffer_is_empty(const xpt8871_ring_buffer_t *rb) {
    return rb->head == rb->tail;
}

static inline uint16_t buffer_count(const xpt8871_ring_buffer_t *rb) {
    return (rb->head - rb->tail) & XPT8871_BUFFER_MASK;
}

static inline uint16_t buffer_free(const xpt8871_ring_buffer_t *rb) {
    return (XPT8871_BUFFER_SIZE - 1U) - buffer_count(rb);
}

static inline bool buffer_pop(xpt8871_ring_buffer_t *rb, uint8_t *sample) {
    if (rb->head == rb->tail) {
        return false;
    }
    *sample = rb->data[rb->tail];
    rb->tail = (rb->tail + 1U) & XPT8871_BUFFER_MASK;
    return true;
}

/* Ініціалізація драйвера XPT8871 */
bool xpt8871_init(xpt8871_t *dev, const xpt8871_hw_config_t *config, uint32_t sample_rate_hz) {
    if (dev == NULL || config == NULL || sample_rate_hz == 0U) {
        return false;
    }

    dev->config = *config;
    dev->sample_rate_hz = sample_rate_hz;
    dev->buffer.head = 0U;
    dev->buffer.tail = 0U;
    dev->state = XPT8871_STATE_SLEEP;
    dev->wakeup_ticks_remaining = 0U;
    dev->idle_ticks_remaining = 0U;

    /* Початковий безпечний стан: SHDN = LOW для запобігання клацанням при старті живлення МК */
    HAL_GPIO_WritePin(dev->config.shdn_port, dev->config.shdn_pin, GPIO_PIN_RESET);

    /* Ініціалізація ЦАП на рівень постійного зміщення тиші (Vdd / 2) */
    HAL_DAC_Start(dev->config.hdac, dev->config.dac_channel);
    HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                     DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);

    /* Запуск таймера частоти дискретизації з перериваннями */
    HAL_TIM_Base_Start_IT(dev->config.htim);

    return true;
}

/* Деініціалізація драйвера */
void xpt8871_deinit(xpt8871_t *dev) {
    if (dev == NULL) {
        return;
    }

    xpt8871_stop(dev);
    HAL_TIM_Base_Stop_IT(dev->config.htim);
    HAL_DAC_Stop(dev->config.hdac, dev->config.dac_channel);
}

/* Неблокувальний запис даних у буфер відтворення */
size_t xpt8871_write(xpt8871_t *dev, const uint8_t *samples, size_t count) {
    if (dev == NULL || samples == NULL || count == 0U) {
        return 0U;
    }

    uint16_t available = buffer_free(&dev->buffer);
    size_t to_write = (count < (size_t)available) ? count : (size_t)available;

    for (size_t i = 0U; i < to_write; i++) {
        dev->buffer.data[dev->buffer.head] = samples[i];
        dev->buffer.head = (dev->buffer.head + 1U) & XPT8871_BUFFER_MASK;
    }

    /* Якщо додано нові вибірки, керуємо станом живлення мікросхеми */
    if (to_write > 0U) {
        if (dev->state == XPT8871_STATE_SLEEP) {
            /*
             * Перед увімкненням переконуємося, що ЦАП стабільно видає напругу зміщення.
             * Переводимо SHDN у HIGH та встановлюємо лічильник стабілізації BYPASS.
             */
            HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                             DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);
            HAL_GPIO_WritePin(dev->config.shdn_port, dev->config.shdn_pin, GPIO_PIN_SET);

            dev->wakeup_ticks_remaining = (dev->sample_rate_hz * XPT8871_WAKEUP_DELAY_MS) / 1000U;
            dev->state = XPT8871_STATE_WAKING;
        } else if (dev->state == XPT8871_STATE_IDLE_DRAIN) {
            /* Якщо підсилювач ще не встиг заснути — миттєво повертаємося до гри */
            dev->state = XPT8871_STATE_PLAYING;
        }
    }

    return to_write;
}

/* Запис одного семпла */
bool xpt8871_write_sample(xpt8871_t *dev, uint8_t sample) {
    return xpt8871_write(dev, &sample, 1U) == 1U;
}

/* Отримання обсягу вільного місця в кільцевому буфері */
size_t xpt8871_get_free_space(const xpt8871_t *dev) {
    if (dev == NULL) {
        return 0U;
    }
    return (size_t)buffer_free(&dev->buffer);
}

/* Перевірка активності відтворення */
bool xpt8871_is_playing(const xpt8871_t *dev) {
    if (dev == NULL) {
        return false;
    }
    return (dev->state != XPT8871_STATE_SLEEP) || !buffer_is_empty(&dev->buffer);
}

/* Примусова зупинка відтворення */
void xpt8871_stop(xpt8871_t *dev) {
    if (dev == NULL) {
        return;
    }

    /* Скидання кільцевого буфера */
    dev->buffer.tail = dev->buffer.head;

    /* Вимикання вихідних каскадів мікросхеми та повернення ЦАП до зміщення */
    HAL_GPIO_WritePin(dev->config.shdn_port, dev->config.shdn_pin, GPIO_PIN_RESET);
    HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                     DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);

    dev->state = XPT8871_STATE_SLEEP;
    dev->wakeup_ticks_remaining = 0U;
    dev->idle_ticks_remaining = 0U;
}

/* Обробник таймерних переривань видачі аудіосемплів */
void xpt8871_timer_isr(xpt8871_t *dev) {
    if (dev == NULL) {
        return;
    }

    switch (dev->state) {
        case XPT8871_STATE_SLEEP:
            /* Підсилювач вимкнений, вихід не оновлюється */
            break;

        case XPT8871_STATE_WAKING:
            /*
             * Утримуємо нульову змінну складову (рівень зміщення VDD/2),
             * поки перехідний процес заряду BYPASS-конденсатора не завершиться.
             */
            HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                             DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);
            if (dev->wakeup_ticks_remaining > 0U) {
                dev->wakeup_ticks_remaining--;
            } else {
                dev->state = XPT8871_STATE_PLAYING;
            }
            break;

        case XPT8871_STATE_PLAYING: {
            uint8_t sample;
            if (buffer_pop(&dev->buffer, &sample)) {
                /* Вибірка присутня в буфері — записуємо її в регістр ЦАП */
                HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                                 DAC_ALIGN_8B_R, sample);
            } else {
                /*
                 * Буфер вичерпано: повертаємо ЦАП на рівень зміщення і запускаємо
                 * таймаут очікування перед переведенням мікросхеми в сон.
                 */
                HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                                 DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);
                dev->idle_ticks_remaining = (dev->sample_rate_hz * XPT8871_IDLE_TIMEOUT_MS) / 1000U;
                dev->state = XPT8871_STATE_IDLE_DRAIN;
            }
            break;
        }

        case XPT8871_STATE_IDLE_DRAIN: {
            uint8_t sample;
            if (buffer_pop(&dev->buffer, &sample)) {
                /* Якщо новий пакет семплів підійшов до вичерпання таймауту */
                HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                                 DAC_ALIGN_8B_R, sample);
                dev->state = XPT8871_STATE_PLAYING;
            } else {
                HAL_DAC_SetValue(dev->config.hdac, dev->config.dac_channel,
                                 DAC_ALIGN_8B_R, XPT8871_SAMPLE_BIAS);
                if (dev->idle_ticks_remaining > 0U) {
                    dev->idle_ticks_remaining--;
                } else {
                    /*
                     * Таймаут сплив: переводимо XPT8871 у глибокий сон (SHDN = LOW).
                     * Це вимикає вихідні каскади й прибирає фоновий шум спокою.
                     */
                    HAL_GPIO_WritePin(dev->config.shdn_port, dev->config.shdn_pin, GPIO_PIN_RESET);
                    dev->state = XPT8871_STATE_SLEEP;
                }
            }
            break;
        }
    }
}
