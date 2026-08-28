    while (1) {                                  // продовження main
        if (!irqTriggered) continue;             // подій немає — нічого не робимо
        irqTriggered = false;                    // скинути прапорець одразу

        HAL_Delay(2);                            // ← КРИТИЧНО: дати чіпу досипати

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

            if (dist == 1)       printf("БЛИСКАВКА! гроза прямо над головою\r\n");
            else if (dist == 63) printf("БЛИСКАВКА! надто далеко для оцінки\r\n");
            else                 printf("БЛИСКАВКА! ~%u км до фронту грози\r\n", dist);
            printf("енергія розряду (сире число): %lu\r\n", (unsigned long)energy);

        } else if (src == 0x04) {                // 0b0100 = завада від техніки
            printf("Завада (disturber) — поруч щось шумить\r\n");

        } else if (src == 0x01) {                // 0b0001 = зависокий шум
            printf("Шум зависокий — підніми поріг або віднеси давач\r\n");

        } else {                                 // 0 = неочікувано
            printf("Переривання без зрозумілої причини\r\n");
        }
    }
}
