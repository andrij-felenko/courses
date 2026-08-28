#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Стани з'єднання радіоканалу */
typedef enum {
    LINK_STATE_DISCONNECTED = 0,
    LINK_STATE_SEARCHING,
    LINK_STATE_CONNECTED,
    LINK_STATE_HANDOFF_REQUIRED
} link_state_t;

/* Структура конфігурації та стану фільтра RSSI */
typedef struct {
    float alpha;               /* Коефіцієнт згладжування (0.0 < alpha <= 1.0) */
    float filtered_rssi_dbm;   /* Поточне фільтроване значення в дБм */
    bool initialized;          /* Прапорець первинної ініціалізації */
    
    float connect_threshold_dbm; /* Поріг підключення (наприклад, -85.0 дБм) */
    float disconnect_threshold_dbm; /* Поріг відключення з гістерезисом (наприклад, -95.0 дБм) */
    float handoff_margin_dbm;    /* Запас гістерезису для хендовера (наприклад, 5.0 дБ) */
    
    link_state_t current_state;  /* Поточний стан лінку */
} rssi_filter_t;

/**
 * @brief Ініціалізація структури фільтра
 */
void rssi_filter_init(rssi_filter_t *filter, float alpha, 
                      float connect_th, float disconnect_th, float handoff_margin) {
    if (!filter) return;
    
    filter->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.2f;
    filter->filtered_rssi_dbm = -120.0f;
    filter->initialized = false;
    filter->connect_threshold_dbm = connect_th;
    filter->disconnect_threshold_dbm = disconnect_th;
    filter->handoff_margin_dbm = handoff_margin;
    filter->current_state = LINK_STATE_DISCONNECTED;
}

/**
 * @brief Оновлення стану фільтра новим сирим відліком RSSI
 * @param filter Вказівник на структуру
 * @param raw_rssi_dbm Сире виміряне значення з АЦП/демодулятора у дБм
 * @param neighbor_rssi_dbm Поточний рівень сигналу сусідньої вежі
 * @return Поточний оновлений стан лінку
 */
link_state_t rssi_filter_update(rssi_filter_t *filter, float raw_rssi_dbm, float neighbor_rssi_dbm) {
    if (!filter) return LINK_STATE_DISCONNECTED;

    /* 1. Експоненційне ковзне середнє (IIR / EMA фільтр) */
    if (!filter->initialized) {
        filter->filtered_rssi_dbm = raw_rssi_dbm;
        filter->initialized = true;
    } else {
        filter->filtered_rssi_dbm = (filter->alpha * raw_rssi_dbm) + 
                                    ((1.0f - filter->alpha) * filter->filtered_rssi_dbm);
    }

    /* 2. Логіка кінцевого автомата станів (FSM) із гістерезисом */
    switch (filter->current_state) {
        case LINK_STATE_DISCONNECTED:
            if (filter->filtered_rssi_dbm >= filter->connect_threshold_dbm) {
                filter->current_state = LINK_STATE_CONNECTED;
            } else {
                filter->current_state = LINK_STATE_SEARCHING;
            }
            break;

        case LINK_STATE_SEARCHING:
            if (filter->filtered_rssi_dbm >= filter->connect_threshold_dbm) {
                filter->current_state = LINK_STATE_CONNECTED;
            }
            break;

        case LINK_STATE_CONNECTED:
            /* Поріг відключення нижчий за поріг підключення (гістерезис) */
            if (filter->filtered_rssi_dbm < filter->disconnect_threshold_dbm) {
                filter->current_state = LINK_STATE_DISCONNECTED;
            }
            /* Перевірка потреби хендовера на сусідній осередки */
            else if (neighbor_rssi_dbm > (filter->filtered_rssi_dbm + filter->handoff_margin_dbm)) {
                filter->current_state = LINK_STATE_HANDOFF_REQUIRED;
            }
            break;

        case LINK_STATE_HANDOFF_REQUIRED:
            /* Статус скидається після виконання процедури перемикання */
            if (neighbor_rssi_dbm <= (filter->filtered_rssi_dbm + filter->handoff_margin_dbm)) {
                filter->current_state = LINK_STATE_CONNECTED;
            }
            break;
    }

    return filter->current_state;
}

int main(void) {
    rssi_filter_t filter;
    rssi_filter_init(&filter, 0.15f, -80.0f, -92.0f, 6.0f);

    /* Симуляція серії відліків сигналу (згасання + шум) */
    float raw_samples[] = {
        -110.0f, -105.0f, -82.0f, -78.0f, -75.0f, -74.0f, /* Вхід у покриття */
        -76.0f,  -90.0f,  -73.0f, -75.0f,                /* Швидке завмирання */
        -88.0f,  -94.0f,  -96.0f, -98.0f                 /* Вихід із покриття */
    };
    size_t sample_count = sizeof(raw_samples) / sizeof(raw_samples[0]);

    printf("Крок | Сирий (дБм) | Фільтрований (дБм) | Стан лінку\n");
    printf("---------------------------------------------------\n");

    for (size_t i = 0; i < sample_count; ++i) {
        link_state_t state = rssi_filter_update(&filter, raw_samples[i], -120.0f);
        const char *state_str = (state == LINK_STATE_CONNECTED) ? "CONNECTED" :
                                (state == LINK_STATE_SEARCHING) ? "SEARCHING" :
                                (state == LINK_STATE_HANDOFF_REQUIRED) ? "HANDOFF" : "DISCONNECTED";
        
        printf("%4zu | %11.1f | %17.2f | %s\n", 
               i + 1, raw_samples[i], filter->filtered_rssi_dbm, state_str);
    }

    return 0;
}
