    while (1) {                                  // продовження app_main
        if (!irq_triggered) {                    // подій немає — віддати такт іншим
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        irq_triggered = false;                   // скинути прапорець одразу

        vTaskDelay(pdMS_TO_TICKS(2));            // ← КРИТИЧНО: дати чіпу досипати

        uint8_t src;
        as3935_read(0x03, &src);                 // читання скидає IRQ у низький
        src &= 0x0F;                             // сирі біти чіпа: 8 / 4 / 1

        if (src == 0x08) {                       // 0b1000 = блискавка
            uint8_t dist, e0, e1, e2;
            as3935_read(0x07, &dist);  dist &= 0x3F;
            as3935_read(0x04, &e0);              // енергія: 0x04 + 0x05 + 0x06[4:0]
            as3935_read(0x05, &e1);
            as3935_read(0x06, &e2);
            uint32_t energy = ((uint32_t)(e2 & 0x1F) << 16) | ((uint32_t)e1 << 8) | e0;

            if (dist == 1)       ESP_LOGI(TAG, "БЛИСКАВКА! гроза прямо над головою");
            else if (dist == 63) ESP_LOGI(TAG, "БЛИСКАВКА! надто далеко для оцінки");
            else                 ESP_LOGI(TAG, "БЛИСКАВКА! ~%u км до фронту грози", dist);
            ESP_LOGI(TAG, "енергія розряду (сире число): %lu", (unsigned long)energy);

        } else if (src == 0x04) {                // 0b0100 = завада від техніки
            ESP_LOGW(TAG, "Завада (disturber) — поруч щось шумить");

        } else if (src == 0x01) {                // 0b0001 = зависокий шум
            ESP_LOGW(TAG, "Шум зависокий — підніми поріг або віднеси давач");

        } else {                                 // 0 = неочікувано
            ESP_LOGW(TAG, "Переривання без зрозумілої причини");
        }
    }
}
